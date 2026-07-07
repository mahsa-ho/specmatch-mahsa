from fastapi import APIRouter, Query

from app.core.db import get_conn
from app.models.schemas import RecordOut, RecordsResponse

router = APIRouter()


@router.get("/records", response_model=RecordsResponse)
def list_records(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> RecordsResponse:
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) AS n FROM records").fetchone()["n"]
        rows = conn.execute(
            "SELECT record_id, raw_text, category, unit, quantity, ingested_at"
            " FROM records ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
    finally:
        conn.close()
    items = [
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
    return RecordsResponse(total=total, items=items)
