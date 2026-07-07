def test_matches_endpoints_are_stubbed(client):
    """Task 4 replaces these expectations with real contract tests."""
    assert client.get("/matches").status_code == 501
    resp = client.post("/matches/SRC-0001/review", json={"action": "accept"})
    assert resp.status_code == 501
