"""Server-rendered review console (Jinja2)."""

from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core.db import get_conn
from app.models.schemas import MatchResult
from app.services.matching.engine import LexicalMatchingEngine

router = APIRouter()

templates = Jinja2Templates(directory=Path(__file__).resolve().parents[1] / "templates")


@router.get("/", response_class=HTMLResponse)
def record_table(request: Request, category: str | None = Query(default=None)):
    conn = get_conn()
    try:
        categories = [
            row["category"]
            for row in conn.execute(
                "SELECT DISTINCT category FROM records"
                " WHERE category IS NOT NULL AND category != '' ORDER BY category"
            ).fetchall()
        ]

        if category and category != "All categories":
            rows = conn.execute(
                "SELECT record_id, raw_text, category, unit, quantity FROM records"
                " WHERE category = ? ORDER BY id",
                (category,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT record_id, raw_text, category, unit, quantity FROM records"
                " ORDER BY id"
            ).fetchall()
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "records.html",
        {
            "records": rows,
            "categories": categories,
            "selected_category": category,
        },
    )


@router.get("/review", response_class=HTMLResponse)
def review_panel(
    request: Request,
    tier: str | None = Query(default=None),
):
    conn = get_conn()
    try:
        match_count = conn.execute("SELECT COUNT(*) AS n FROM matches").fetchone()["n"]

        if match_count == 0:
            LexicalMatchingEngine(conn=conn).match_all()

        tier_counts = {
            "green": 0,
            "yellow": 0,
            "red": 0,
        }

        for row in conn.execute(
            "SELECT tier, COUNT(*) AS n FROM matches GROUP BY tier"
        ).fetchall():
            tier_counts[row["tier"]] = row["n"]

        selected_tier = tier if tier in {"green", "yellow", "red"} else None

        if selected_tier:
            rows = conn.execute(
                "SELECT payload FROM matches WHERE tier = ? ORDER BY record_id",
                (selected_tier,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT payload FROM matches ORDER BY record_id"
            ).fetchall()

        matches = [
            MatchResult.model_validate_json(row["payload"]).model_dump(mode="json")
            for row in rows
        ]
    finally:
        conn.close()

    return templates.TemplateResponse(
        request,
        "review.html",
        {
            "matches": matches,
            "tier_counts": tier_counts,
            "selected_tier": selected_tier or "all",
        },
    )