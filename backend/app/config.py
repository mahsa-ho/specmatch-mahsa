"""Application settings, loaded from config/settings.yaml.

Scoring weights and tier thresholds live in the YAML file, never in code.
Override the file location with the SPECMATCH_CONFIG environment variable.
"""

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from app.core.errors import DependencyError
from app.core.logging import log_event

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class TierThresholds:
    """Score boundaries between tiers. Both bounds are inclusive lower bounds."""

    accept_min: float
    review_min: float


@dataclass(frozen=True)
class MatchingSettings:
    top_k: int
    weights: dict[str, float]


@dataclass(frozen=True)
class Settings:
    matching: MatchingSettings
    tiers: TierThresholds


def config_path() -> Path:
    override = os.environ.get("SPECMATCH_CONFIG")
    if override:
        return Path(override)
    return REPO_ROOT / "config" / "settings.yaml"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    path = config_path()
    try:
        with path.open("r", encoding="utf-8") as fh:
            raw = yaml.safe_load(fh)
    except OSError as exc:
        log_event(
            logger,
            logging.ERROR,
            "dependency_failure",
            dependency="filesystem",
            path=str(path),
            error=str(exc),
        )
        raise DependencyError(f"could not read settings file: {path}") from exc

    matching = raw["matching"]
    tiers = raw["tiers"]
    return Settings(
        matching=MatchingSettings(
            top_k=int(matching["top_k"]),
            weights={k: float(v) for k, v in matching["weights"].items()},
        ),
        tiers=TierThresholds(
            accept_min=float(tiers["accept_min"]),
            review_min=float(tiers["review_min"]),
        ),
    )
