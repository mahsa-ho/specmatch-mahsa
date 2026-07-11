"""Match endpoints."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.core.db import get_conn
from app.models.schemas import MatchResult, MatchesResponse, Review, ReviewAction, ReviewRequest, Tier
from app.services.matching.engine import LexicalMatchingEngine


router = APIRouter()


def _decode_match(row: sqlite3.Row) -> MatchResult:
    return MatchResult.model_validate_json(row["payload"])


def _persist_match(conn: sqlite3.Connection, result: MatchResult) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO matches (record_id, payload, tier, matched_at) "
        "VALUES (?, ?, ?, ?)",
        (
            result.record_id,
            result.model_dump_json(),
            result.tier.value,
            result.matched_at.isoformat(),
        ),
    )
    conn.commit()


def _ensure_matches_exist(conn: sqlite3.Connection) -> None:
    count = conn.execute("SELECT COUNT(*) AS n FROM matches").fetchone()["n"]
    if count == 0:
        LexicalMatchingEngine(conn=conn).match_all()


def _ensure_review_audit_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS review_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT NOT NULL,
            action TEXT NOT NULL,
            catalog_id TEXT,
            note TEXT,
            reviewed_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


@router.get("/matches", response_model=MatchesResponse)
def list_matches(
    tier: Tier | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> MatchesResponse:
    conn = get_conn()
    try:
        _ensure_matches_exist(conn)

        where = ""
        params: list[object] = []

        if tier is not None:
            where = "WHERE tier = ?"
            params.append(tier.value)

        total = conn.execute(
            f"SELECT COUNT(*) AS n FROM matches {where}",
            params,
        ).fetchone()["n"]

        rows = conn.execute(
            f"SELECT payload FROM matches {where} ORDER BY record_id LIMIT ? OFFSET ?",
            [*params, limit, offset],
        ).fetchall()

        items = [_decode_match(row) for row in rows]
        return MatchesResponse(total=total, items=items)
    finally:
        conn.close()


@router.post("/matches/{record_id}/review", response_model=MatchResult)
def review_match(record_id: str, body: ReviewRequest) -> MatchResult:
    conn = get_conn()
    try:
        _ensure_matches_exist(conn)

        row = conn.execute(
            "SELECT payload FROM matches WHERE record_id = ?",
            (record_id,),
        ).fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Match not found")

        result = _decode_match(row)

        if body.action is ReviewAction.override and not body.catalog_id:
            raise HTTPException(
                status_code=400,
                detail="catalog_id is required for override reviews",
            )

        if body.action is ReviewAction.accept:
            selected_catalog_id = body.catalog_id
            if selected_catalog_id is None and result.candidates:
                selected_catalog_id = result.candidates[0].catalog_id
        elif body.action is ReviewAction.override:
            selected_catalog_id = body.catalog_id
        else:
            selected_catalog_id = None

        review = Review(
            action=body.action,
            catalog_id=body.catalog_id,
            note=body.note,
            reviewed_at=datetime.now(timezone.utc),
        )

        updated = result.model_copy(
            update={
                "selected_catalog_id": selected_catalog_id,
                "review": review,
            }
        )

        _persist_match(conn, updated)

        _ensure_review_audit_table(conn)
        conn.execute(
            "INSERT INTO review_events (record_id, action, catalog_id, note, reviewed_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                record_id,
                body.action.value,
                body.catalog_id,
                body.note,
                review.reviewed_at.isoformat(),
            ),
        )
        conn.commit()

        return updated
    finally:
        conn.close()