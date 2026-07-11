from app.services.matching.engine import LexicalMatchingEngine


def test_matches_endpoint_returns_persisted_matches(client):
    LexicalMatchingEngine().match_all()

    response = client.get("/matches", params={"limit": 5, "offset": 0})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 150
    assert len(body["items"]) == 5

    first = body["items"][0]
    assert first["record_id"].startswith("SRC-")
    assert first["source_text"]
    assert first["tier"] in {"green", "yellow", "red"}
    assert first["candidates"]


def test_matches_endpoint_filters_by_tier(client):
    LexicalMatchingEngine().match_all()

    all_matches = client.get("/matches").json()["items"]
    tier = all_matches[0]["tier"]

    response = client.get("/matches", params={"tier": tier})

    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert all(item["tier"] == tier for item in body["items"])


def test_review_endpoint_persists_decision(client):
    LexicalMatchingEngine().match_all()

    first = client.get("/matches", params={"limit": 1}).json()["items"][0]
    record_id = first["record_id"]
    catalog_id = first["candidates"][0]["catalog_id"]

    response = client.post(
        f"/matches/{record_id}/review",
        json={
            "action": "accept",
            "catalog_id": catalog_id,
            "note": "Reviewed during API test",
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["record_id"] == record_id
    assert updated["selected_catalog_id"] == catalog_id
    assert updated["review"]["action"] == "accept"
    assert updated["review"]["catalog_id"] == catalog_id
    assert updated["review"]["note"] == "Reviewed during API test"

    again = client.get("/matches", params={"limit": 1}).json()["items"][0]
    assert again["review"]["action"] == "accept"