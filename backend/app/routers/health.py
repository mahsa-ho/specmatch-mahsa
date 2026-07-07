from fastapi import APIRouter

from app.core.db import get_conn
from app.models.schemas import HealthResponse, TierCounts

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    conn = get_conn()
    try:
        records = conn.execute("SELECT COUNT(*) AS n FROM records").fetchone()["n"]
        matched = conn.execute("SELECT COUNT(*) AS n FROM matches").fetchone()["n"]
        tier_rows = conn.execute(
            "SELECT tier, COUNT(*) AS n FROM matches GROUP BY tier"
        ).fetchall()
    finally:
        conn.close()
    tiers = TierCounts(**{row["tier"]: row["n"] for row in tier_rows})
    return HealthResponse(status="ok", records=records, matched=matched, tiers=tiers)
