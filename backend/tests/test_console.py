def test_record_table_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "SRC-" in resp.text


def test_category_filter_narrows_results(client):
    resp = client.get("/", params={"category": "Concrete"})
    assert resp.status_code == 200
    assert "CONC" in resp.text
    assert "GYP BD" not in resp.text

def test_empty_category_filter_shows_all_records(client):
    response = client.get("/", params={"category": ""})

    assert response.status_code == 200
    assert "150 record(s)" in response.text
    assert "SRC-0001" in response.text

    from app.services.matching.engine import LexicalMatchingEngine


def test_review_console_shows_matches_and_counts(client):
    LexicalMatchingEngine().match_all()

    response = client.get("/review")

    assert response.status_code == 200
    assert "Review Console" in response.text
    assert "Tier counts" in response.text
    assert "Source text" in response.text
    assert "Candidates" in response.text


def test_review_console_can_filter_by_tier(client):
    LexicalMatchingEngine().match_all()

    response = client.get("/review", params={"tier": "yellow"})

    assert response.status_code == 200
    assert "Review Console" in response.text
    assert "yellow" in response.text