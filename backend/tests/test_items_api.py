def test_list_items_empty(authed_client):
    resp = authed_client.get("/api/items")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_item(authed_client):
    resp = authed_client.post("/api/items", json={"name": "Milk"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Milk"
    assert data["category_id"] is None


def test_create_item_with_category(authed_client):
    cat = authed_client.post("/api/categories", json={"name": "Dairy"}).json()
    resp = authed_client.post("/api/items", json={"name": "Milk", "category_id": cat["id"]})
    assert resp.status_code == 200
    assert resp.json()["category_id"] == cat["id"]


def test_update_item(authed_client):
    item = authed_client.post("/api/items", json={"name": "Milk"}).json()
    resp = authed_client.put(f"/api/items/{item['id']}", json={"name": "Whole Milk"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Whole Milk"


def test_delete_item(authed_client):
    item = authed_client.post("/api/items", json={"name": "Milk"}).json()
    resp = authed_client.delete(f"/api/items/{item['id']}")
    assert resp.status_code == 200
    assert authed_client.get("/api/items").json() == []


def test_items_sorted_by_name(authed_client):
    authed_client.post("/api/items", json={"name": "Zebra"})
    authed_client.post("/api/items", json={"name": "Apple"})
    authed_client.post("/api/items", json={"name": "Mango"})
    names = [i["name"] for i in authed_client.get("/api/items").json()]
    assert names == ["Apple", "Mango", "Zebra"]


def test_update_nonexistent_item(authed_client):
    resp = authed_client.put("/api/items/9999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_delete_nonexistent_item(authed_client):
    resp = authed_client.delete("/api/items/9999")
    assert resp.status_code == 404


def test_bulk_delete_items(authed_client):
    a = authed_client.post("/api/items", json={"name": "A"}).json()
    b = authed_client.post("/api/items", json={"name": "B"}).json()
    c = authed_client.post("/api/items", json={"name": "C"}).json()
    resp = authed_client.post("/api/items/delete", json={"ids": [a["id"], b["id"]]})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert resp.json()["deleted"] == 2
    remaining = authed_client.get("/api/items").json()
    assert len(remaining) == 1
    assert remaining[0]["id"] == c["id"]


def test_bulk_delete_empty_ids(authed_client):
    resp = authed_client.post("/api/items/delete", json={"ids": []})
    assert resp.status_code == 200
    assert resp.json()["deleted"] == 0


def test_bulk_set_category(authed_client):
    cat = authed_client.post("/api/categories", json={"name": "Dairy"}).json()
    a = authed_client.post("/api/items", json={"name": "A"}).json()
    b = authed_client.post("/api/items", json={"name": "B"}).json()
    resp = authed_client.post("/api/items/set-category", json={
        "item_ids": [a["id"], b["id"]],
        "category_id": cat["id"]
    })
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
    assert resp.json()["updated"] == 2
    items = authed_client.get("/api/items").json()
    for item in items:
        assert item["category_id"] == cat["id"]


def test_bulk_set_category_to_null(authed_client):
    cat = authed_client.post("/api/categories", json={"name": "Dairy"}).json()
    a = authed_client.post("/api/items", json={"name": "A", "category_id": cat["id"]}).json()
    resp = authed_client.post("/api/items/set-category", json={
        "item_ids": [a["id"]],
        "category_id": None
    })
    assert resp.status_code == 200
    assert resp.json()["updated"] == 1
    items = authed_client.get("/api/items").json()
    assert items[0]["category_id"] is None


def test_bulk_set_category_nonexistent(authed_client):
    a = authed_client.post("/api/items", json={"name": "A"}).json()
    resp = authed_client.post("/api/items/set-category", json={
        "item_ids": [a["id"]],
        "category_id": 9999
    })
    assert resp.status_code == 404


def test_merge_items_redirects_shopping_list(authed_client, db_session):
    item_a = authed_client.post("/api/items", json={"name": "A"}).json()
    item_b = authed_client.post("/api/items", json={"name": "B"}).json()
    authed_client.post("/api/list/add", json={"items": [{"item_id": item_b["id"], "quantity": 2}]})

    resp = authed_client.post(f"/api/items/{item_a['id']}/merge", json={"source_ids": [item_b["id"]]})
    assert resp.status_code == 200

    list_items = authed_client.get("/api/list").json()
    assert len(list_items) == 1
    assert list_items[0]["item_id"] == item_a["id"]


def test_merge_items_redirects_recipe_items(authed_client):
    item_a = authed_client.post("/api/items", json={"name": "A"}).json()
    item_b = authed_client.post("/api/items", json={"name": "B"}).json()
    authed_client.post("/api/recipes", json={"name": "R1", "items": [{"item_id": item_b["id"], "quantity": 1}]})

    authed_client.post(f"/api/items/{item_a['id']}/merge", json={"source_ids": [item_b["id"]]})

    recipes = authed_client.get("/api/recipes").json()
    assert recipes[0]["recipe_items"][0]["item_id"] == item_a["id"]


def test_merge_items_redirects_session_items(authed_client):
    item_a = authed_client.post("/api/items", json={"name": "A"}).json()
    item_b = authed_client.post("/api/items", json={"name": "B"}).json()
    authed_client.post("/api/list/add", json={"items": [{"item_id": item_b["id"], "quantity": 1}]})
    authed_client.post("/api/session/start")

    authed_client.post(f"/api/items/{item_a['id']}/merge", json={"source_ids": [item_b["id"]]})

    session = authed_client.get("/api/session/active").json()
    assert session["session_items"][0]["item_id"] == item_a["id"]


def test_merge_deletes_source_items(authed_client):
    item_a = authed_client.post("/api/items", json={"name": "A"}).json()
    item_b = authed_client.post("/api/items", json={"name": "B"}).json()
    authed_client.post(f"/api/items/{item_a['id']}/merge", json={"source_ids": [item_b["id"]]})
    items = authed_client.get("/api/items").json()
    assert len(items) == 1
    assert items[0]["id"] == item_a["id"]


def test_merge_nonexistent_target(authed_client):
    resp = authed_client.post("/api/items/9999/merge", json={"source_ids": [1]})
    assert resp.status_code == 404


def test_merge_self_returns_item(authed_client):
    item = authed_client.post("/api/items", json={"name": "A"}).json()
    resp = authed_client.post(f"/api/items/{item['id']}/merge", json={"source_ids": [item["id"]]})
    assert resp.status_code == 200
    assert resp.json()["id"] == item["id"]


def test_merge_empty_sources(authed_client):
    item = authed_client.post("/api/items", json={"name": "A"}).json()
    resp = authed_client.post(f"/api/items/{item['id']}/merge", json={"source_ids": []})
    assert resp.status_code == 200
