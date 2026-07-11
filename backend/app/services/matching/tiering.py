"""Tier assignment from composite confidence scores."""

from app.config import TierThresholds
from app.models.schemas import Tier


def assign_tier(score: float, thresholds: TierThresholds) -> Tier:
    """Map a composite score in [0, 1] to a confidence tier.

    Both thresholds are inclusive lower bounds (see config/settings.yaml):
    a score of at least `accept_min` is green, a score of at least
    `review_min` is yellow, anything below is red.
    """
    if score >= thresholds.accept_min:
        return Tier.green
    if score >= thresholds.review_min:
        return Tier.yellow
    return Tier.red
def test_accept_threshold_boundary_is_green():
    assert assign_tier(0.85, THRESHOLDS) is Tier.green


def test_review_threshold_boundary_is_yellow():
    assert assign_tier(0.60, THRESHOLDS) is Tier.yellow