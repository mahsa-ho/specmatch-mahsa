def test_records_returns_ingested_fixture(client):
    resp = client.get("/records")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 150
    assert len(body["items"]) == 50  # default page size
    first = body["items"][0]
    assert set(first) == {
        "record_id",
        "raw_text",
        "category",
        "unit",
        "quantity",
        "ingested_at",
    }


def test_records_pagination(client):
    page1 = client.get("/records", params={"limit": 10, "offset": 0}).json()
    page2 = client.get("/records", params={"limit": 10, "offset": 10}).json()
    ids1 = {item["record_id"] for item in page1["items"]}
    ids2 = {item["record_id"] for item in page2["items"]}
    assert len(ids1) == 10
    assert ids1.isdisjoint(ids2)
