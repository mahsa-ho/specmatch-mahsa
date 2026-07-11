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

    matches = client.get("/matches", params={"limit": 150}).json()["items"]
    assert any(item["record_id"] == record.record_id for item in matches)


def test_matching_engine_matches_all_records(client):
    engine = LexicalMatchingEngine()
    results = engine.match_all()

    assert len(results) == 150
    assert all(result.candidates for result in results)

    matches = client.get("/matches", params={"limit": 150}).json()["items"]
    assert len(matches) == 150

    health = client.get("/health").json()
    assert health["matched"] == 150
    assert sum(health["tiers"].values()) == 150
    from datetime import datetime, timezone


def test_obvious_concrete_record_lands_green_or_yellow(client):
    record = RecordOut(
        record_id="TEST-CONC-001",
        raw_text="CONC RM 30MPa w/ 25% FA",
        category="Concrete",
        unit="m3",
        quantity=1,
        ingested_at=datetime.now(timezone.utc),
    )

    result = LexicalMatchingEngine().match_record(record)

    assert result.candidates
    assert result.tier.value in {"green", "yellow"}
    assert "concrete" in result.candidates[0].description.lower()


def test_unknown_material_lands_red(client):
    record = RecordOut(
        record_id="TEST-RED-001",
        raw_text="ZZZ UNKNOWN RANDOM MATERIAL QQQ",
        category="Unknown",
        unit="banana",
        quantity=1,
        ingested_at=datetime.now(timezone.utc),
    )

    result = LexicalMatchingEngine().match_record(record)

    assert result.candidates
    assert result.tier.value == "red"