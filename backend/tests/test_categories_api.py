def test_list_categories_empty(authed_client):
    resp = authed_client.get("/api/categories")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_category(authed_client):
    resp = authed_client.post("/api/categories", json={"name": "Dairy"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Dairy"
    assert data["color"] == "#6b7280"
    assert "id" in data


def test_create_category_with_color(authed_client):
    resp = authed_client.post("/api/categories", json={"name": "Produce", "color": "#22c55e"})
    assert resp.status_code == 200
    assert resp.json()["color"] == "#22c55e"


def test_update_category(authed_client):
    create = authed_client.post("/api/categories", json={"name": "Dairy"})
    cat_id = create.json()["id"]
    resp = authed_client.put(f"/api/categories/{cat_id}", json={"name": "Dairy Products"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Dairy Products"


def test_partial_update_category(authed_client):
    create = authed_client.post("/api/categories", json={"name": "Dairy", "color": "#ff0000"})
    cat_id = create.json()["id"]
    resp = authed_client.put(f"/api/categories/{cat_id}", json={"color": "#00ff00"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Dairy"
    assert resp.json()["color"] == "#00ff00"


def test_delete_category(authed_client):
    create = authed_client.post("/api/categories", json={"name": "Dairy"})
    cat_id = create.json()["id"]
    resp = authed_client.delete(f"/api/categories/{cat_id}")
    assert resp.status_code == 200
    assert authed_client.get("/api/categories").json() == []


def test_categories_sorted_by_name(authed_client):
    authed_client.post("/api/categories", json={"name": "Zebra"})
    authed_client.post("/api/categories", json={"name": "Apple"})
    authed_client.post("/api/categories", json={"name": "Mango"})
    resp = authed_client.get("/api/categories")
    names = [c["name"] for c in resp.json()]
    assert names == ["Apple", "Mango", "Zebra"]


def test_update_nonexistent_category(authed_client):
    resp = authed_client.put("/api/categories/9999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_category_household_isolation(client, household, second_household, auth_headers, second_auth_headers):
    client.post("/api/categories", json={"name": "H1 Cat"}, headers=auth_headers)
    resp1 = client.get("/api/categories", headers=auth_headers)
    resp2 = client.get("/api/categories", headers=second_auth_headers)
    assert len(resp1.json()) == 1
    assert len(resp2.json()) == 0
