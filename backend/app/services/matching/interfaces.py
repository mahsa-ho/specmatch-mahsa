"""Matching-engine interfaces.

The engine implementation is yours to build, but it must sit behind these
interfaces so alternative retrieval or scoring strategies stay swappable.
Weights and tier thresholds come from Settings (config/settings.yaml) —
never hardcode them.
"""

from abc import ABC, abstractmethod

from app.models.schemas import Candidate, CatalogEntry, MatchResult, RecordOut


class CandidateRetriever(ABC):
    """Finds plausible catalog candidates for one source record."""

    @abstractmethod
    def retrieve(
        self, record: RecordOut, catalog: list[CatalogEntry], limit: int
    ) -> list[CatalogEntry]:
        """Return up to `limit` catalog entries worth scoring for `record`."""


class CandidateScorer(ABC):
    """Scores one candidate against one source record."""

    @abstractmethod
    def score(self, record: RecordOut, entry: CatalogEntry) -> Candidate:
        """Return the candidate with a composite score in [0, 1] and the
        per-signal breakdown that produced it."""


class MatchingEngine(ABC):
    """Orchestrates retrieval, scoring, tier assignment, and persistence."""

    @abstractmethod
    def match_record(self, record: RecordOut) -> MatchResult:
        """Produce (and persist) the MatchResult for one source record."""

    @abstractmethod
    def match_all(self) -> list[MatchResult]:
        """Match every ingested source record."""
