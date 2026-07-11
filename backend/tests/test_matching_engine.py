from app.models.schemas import RecordOut
from app.services.matching.engine import LexicalMatchingEngine


def test_matching_engine_scores_and_persists_one_record(client):
    record_data = client.get("/records", params={"limit": 1}).json()["items"][0]
    record = RecordOut(**record_data)

    engine = LexicalMatchingEngine()
    result = engine.match_record(record)

    assert result.record_id == record.record_id
    assert result.source_text == record.raw_text
    assert result.candidates
    assert len(result.candidates) <= 5
    assert 0.0 <= result.candidates[0].score <= 1.0
    assert result.tier in {"green", "yellow", "red"}

    health = client.get("/health").json()
    assert health["matched"] == 1


def test_matching_engine_matches_all_records(client):
    engine = LexicalMatchingEngine()
    results = engine.match_all()

    assert len(results) == 150
    assert all(result.candidates for result in results)

    health = client.get("/health").json()
    assert health["matched"] == 150
    assert sum(health["tiers"].values()) == 150