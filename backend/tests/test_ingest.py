from app.services.ingest import run_ingest


def test_re_running_ingest_does_not_duplicate_records(client):
    before = client.get("/records", params={"limit": 1}).json()["total"]

    run_ingest()

    after = client.get("/records", params={"limit": 1}).json()["total"]

    assert before == 150
    assert after == before