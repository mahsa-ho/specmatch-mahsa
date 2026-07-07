"""API data contracts.

FROZEN — do not modify this file. CI verifies it is unchanged.
If you believe a contract is wrong, document it in your README instead.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Tier(str, Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


class ReviewAction(str, Enum):
    accept = "accept"
    override = "override"
    reject = "reject"


class CatalogEntry(BaseModel):
    catalog_id: str
    description: str
    category: str
    unit: str


class RecordOut(BaseModel):
    record_id: str
    raw_text: str
    category: str | None = None
    unit: str | None = None
    quantity: str | None = None
    ingested_at: datetime


class RecordsResponse(BaseModel):
    total: int
    items: list[RecordOut]


class Candidate(BaseModel):
    """One scored catalog candidate for a source record."""

    catalog_id: str
    description: str
    score: float = Field(ge=0.0, le=1.0)
    signals: dict[str, float]


class Review(BaseModel):
    """A persisted human review decision."""

    action: ReviewAction
    catalog_id: str | None = None
    note: str | None = None
    reviewed_at: datetime


class MatchResult(BaseModel):
    record_id: str
    source_text: str
    tier: Tier
    candidates: list[Candidate]
    selected_catalog_id: str | None = None
    review: Review | None = None
    matched_at: datetime


class MatchesResponse(BaseModel):
    total: int
    items: list[MatchResult]


class ReviewRequest(BaseModel):
    action: ReviewAction
    catalog_id: str | None = None
    note: str | None = None


class TierCounts(BaseModel):
    green: int = 0
    yellow: int = 0
    red: int = 0


class HealthResponse(BaseModel):
    status: str
    records: int
    matched: int
    tiers: TierCounts
