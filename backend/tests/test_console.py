def test_record_table_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "SRC-" in resp.text


def test_category_filter_narrows_results(client):
    resp = client.get("/", params={"category": "Concrete"})
    assert resp.status_code == 200
    assert "CONC" in resp.text
    assert "GYP BD" not in resp.text

def test_all_categories_filter_shows_records(client):
    response = client.get("/", params={"category": "All categories"})

    assert response.status_code == 200
    assert "150 record(s)" in response.text
    assert "SRC-0001" in response.text