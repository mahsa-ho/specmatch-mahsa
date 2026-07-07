"""The matching engine. Implementation is yours to build (Task 3).

Design constraints:

- Implement the interfaces in interfaces.py.
- Composite scores combine at least two distinct signals; the weights come
  from Settings.matching.weights (config/settings.yaml).
- Tier assignment goes through tiering.assign_tier with thresholds from
  Settings.tiers.
- Persist the top-k candidates per record (Settings.matching.top_k) with
  enough information to answer: what matched, with what score, from which
  signals, and why it landed in its tier.
"""

from app.models.schemas import MatchResult, RecordOut
from app.services.matching.interfaces import MatchingEngine


class LexicalMatchingEngine(MatchingEngine):
    """Retrieval + scoring over the ingested catalog. Not implemented yet."""

    def match_record(self, record: RecordOut) -> MatchResult:
        raise NotImplementedError("Task 3: implement the matching engine")

    def match_all(self) -> list[MatchResult]:
        raise NotImplementedError("Task 3: implement the matching engine")
