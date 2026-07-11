"""Lexical matching engine for SpecMatch.

This implementation uses a simple, explainable baseline:
- retrieve likely catalog candidates using normalized text similarity
- score each candidate with string similarity, category agreement, and unit compatibility
- assign a tier using thresholds from settings.yaml
- persist the top-k candidates for each record
"""

from __future__ import annotations

import re
import sqlite3
from datetime import datetime, timezone
from difflib import SequenceMatcher

from app.config import Settings, get_settings
from app.core.db import get_conn
from app.models.schemas import Candidate, CatalogEntry, MatchResult, RecordOut, Tier
from app.services.matching.interfaces import CandidateRetriever, CandidateScorer, MatchingEngine
from app.services.matching.tiering import assign_tier


_ABBREVIATIONS = {
    "conc": "concrete",
    "rm": "ready mix",
    "gyp": "gypsum",
    "bd": "board",
    "stl": "steel",
    "bm": "beam",
    "chan": "channel",
    "batt": "batt",
    "insul": "insulation",
    "mw": "mineral wool",
    "cmu": "concrete masonry unit",
    "pnt": "paint",
    "int": "interior",
    "ltx": "latex",
    "asph": "asphalt",
    "pvg": "paving",
    "cu": "copper",
    "lbr": "lumber",
    "plywd": "plywood",
    "dfir": "douglas fir",
    "emt": "electrical metallic tubing",
    "porc": "porcelain",
    "gran": "granular",
    "misc": "miscellaneous",
    "mtl": "metal",
    "fa": "fly ash",
    "mpa": "mpa",
}


def _normalize(text: str | None) -> str:
    if not text:
        return ""

    value = text.lower()
    value = value.replace("w/", " with ")
    value = value.replace("#", " number ")

    for short, long in _ABBREVIATIONS.items():
        value = re.sub(rf"\b{re.escape(short)}\b", long, value)

    value = re.sub(r"[^a-z0-9./]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _tokens(text: str | None) -> set[str]:
    return set(_normalize(text).split())


def _token_similarity(left: str | None, right: str | None) -> float:
    left_tokens = _tokens(left)
    right_tokens = _tokens(right)

    if not left_tokens or not right_tokens:
        return 0.0

    overlap = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return overlap / union


def _string_similarity(left: str | None, right: str | None) -> float:
    left_norm = _normalize(left)
    right_norm = _normalize(right)

    if not left_norm or not right_norm:
        return 0.0

    sequence_score = SequenceMatcher(None, left_norm, right_norm).ratio()
    token_score = _token_similarity(left_norm, right_norm)
    return (sequence_score * 0.60) + (token_score * 0.40)


def _category_agreement(record: RecordOut, entry: CatalogEntry) -> float:
    if not record.category:
        return 0.50
    return 1.0 if record.category.lower() == entry.category.lower() else 0.0


def _unit_compatibility(record: RecordOut, entry: CatalogEntry) -> float:
    if not record.unit:
        return 0.50
    return 1.0 if record.unit.lower() == entry.unit.lower() else 0.0


class LexicalCandidateRetriever(CandidateRetriever):
    """Find likely catalog candidates using lexical similarity."""

    def retrieve(
        self,
        record: RecordOut,
        catalog: list[CatalogEntry],
        limit: int,
    ) -> list[CatalogEntry]:
        ranked = sorted(
            catalog,
            key=lambda entry: (
                _string_similarity(record.raw_text, entry.description),
                _category_agreement(record, entry),
                _unit_compatibility(record, entry),
            ),
            reverse=True,
        )
        return ranked[:limit]


class WeightedCandidateScorer(CandidateScorer):
    """Score one candidate using configured signal weights."""

    def __init__(self, settings: Settings):
        self.settings = settings

    def score(self, record: RecordOut, entry: CatalogEntry) -> Candidate:
        signals = {
            "string_similarity": _string_similarity(record.raw_text, entry.description),
            "category_agreement": _category_agreement(record, entry),
            "unit_compatibility": _unit_compatibility(record, entry),
        }

        weights = self.settings.matching.weights
        weight_total = sum(weights.values()) or 1.0

        score = sum(signals[name] * weights.get(name, 0.0) for name in signals) / weight_total
        score = max(0.0, min(1.0, score))

        return Candidate(
            catalog_id=entry.catalog_id,
            description=entry.description,
            score=round(score, 4),
            signals={name: round(value, 4) for name, value in signals.items()},
        )


class LexicalMatchingEngine(MatchingEngine):
    """Retrieval + scoring over the ingested catalog."""

    def __init__(
        self,
        conn: sqlite3.Connection | None = None,
        settings: Settings | None = None,
    ):
        self.conn = conn or get_conn()
        self.settings = settings or get_settings()
        self.retriever = LexicalCandidateRetriever()
        self.scorer = WeightedCandidateScorer(self.settings)

    def match_record(self, record: RecordOut) -> MatchResult:
        catalog = self._load_catalog()
        result = self._match_record_against_catalog(record, catalog)
        self._persist(result)
        return result

    def match_all(self) -> list[MatchResult]:
        catalog = self._load_catalog()
        records = self._load_records()

        results = [
            self._match_record_against_catalog(record, catalog)
            for record in records
        ]

        for result in results:
            self._persist(result)

        return results

    def _match_record_against_catalog(
        self,
        record: RecordOut,
        catalog: list[CatalogEntry],
    ) -> MatchResult:
        # Retrieve more than top_k before final scoring so weaker early retrieval
        # does not remove useful candidates too early.
        retrieval_limit = min(len(catalog), max(self.settings.matching.top_k * 5, 10))
        retrieved = self.retriever.retrieve(record, catalog, retrieval_limit)

        scored = sorted(
            [self.scorer.score(record, entry) for entry in retrieved],
            key=lambda candidate: candidate.score,
            reverse=True,
        )

        top_candidates = scored[: self.settings.matching.top_k]
        best_score = top_candidates[0].score if top_candidates else 0.0
        tier = assign_tier(best_score, self.settings.tiers)

        selected_catalog_id = top_candidates[0].catalog_id if tier is Tier.green else None

        return MatchResult(
            record_id=record.record_id,
            source_text=record.raw_text,
            tier=tier,
            candidates=top_candidates,
            selected_catalog_id=selected_catalog_id,
            review=None,
            matched_at=datetime.now(timezone.utc),
        )

    def _load_records(self) -> list[RecordOut]:
        rows = self.conn.execute(
            "SELECT record_id, raw_text, category, unit, quantity, ingested_at "
            "FROM records ORDER BY id"
        ).fetchall()

        return [
            RecordOut(
                record_id=row["record_id"],
                raw_text=row["raw_text"],
                category=row["category"] or None,
                unit=row["unit"] or None,
                quantity=row["quantity"] or None,
                ingested_at=row["ingested_at"],
            )
            for row in rows
        ]

    def _load_catalog(self) -> list[CatalogEntry]:
        rows = self.conn.execute(
            "SELECT catalog_id, description, category, unit "
            "FROM catalog ORDER BY catalog_id"
        ).fetchall()

        return [
            CatalogEntry(
                catalog_id=row["catalog_id"],
                description=row["description"],
                category=row["category"],
                unit=row["unit"],
            )
            for row in rows
        ]

    def _persist(self, result: MatchResult) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO matches (record_id, payload, tier, matched_at) "
            "VALUES (?, ?, ?, ?)",
            (
                result.record_id,
                result.model_dump_json(),
                result.tier.value,
                result.matched_at.isoformat(),
            ),
        )
        self.conn.commit()