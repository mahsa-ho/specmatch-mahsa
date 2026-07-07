"""Match endpoints. Stubbed — completing them to the frozen contracts in
models/schemas.py is Task 4."""

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import MatchesResponse, MatchResult, ReviewRequest, Tier

router = APIRouter()


@router.get("/matches", response_model=MatchesResponse)
def list_matches(
    tier: Tier | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> MatchesResponse:
    # TODO(Task 4): return persisted MatchResults, filterable by tier,
    # shaped as MatchesResponse per models/schemas.py.
    raise HTTPException(status_code=501, detail="Not implemented (Task 4)")


@router.post("/matches/{record_id}/review", response_model=MatchResult)
def review_match(record_id: str, body: ReviewRequest) -> MatchResult:
    # TODO(Task 4): persist the review decision (auditable) and return the
    # updated MatchResult per models/schemas.py.
    raise HTTPException(status_code=501, detail="Not implemented (Task 4)")
