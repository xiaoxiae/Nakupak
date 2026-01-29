def test_list_recipes_empty(authed_client):
    resp = authed_client.get("/api/recipes")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_recipe_without_items(authed_client):
    resp = authed_client.post("/api/recipes", json={"name": "Pancakes"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Pancakes"
    assert data["recipe_items"] == []


def test_create_recipe_with_items(authed_client):
    item = authed_client.post("/api/items", json={"name": "Flour"}).json()
    resp = authed_client.post("/api/recipes", json={
        "name": "Pancakes",
        "items": [{"item_id": item["id"], "quantity": 2}]
    })
    assert resp.status_code == 200
    assert len(resp.json()["recipe_items"]) == 1
    assert resp.json()["recipe_items"][0]["quantity"] == 2


def test_update_recipe_name(authed_client):
    recipe = authed_client.post("/api/recipes", json={"name": "Pancakes"}).json()
    resp = authed_client.put(f"/api/recipes/{recipe['id']}", json={"name": "Waffles"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Waffles"


def test_update_recipe_replaces_items(authed_client):
    item_a = authed_client.post("/api/items", json={"name": "A"}).json()
    item_b = authed_client.post("/api/items", json={"name": "B"}).json()
    recipe = authed_client.post("/api/recipes", json={
        "name": "R1",
        "items": [{"item_id": item_a["id"], "quantity": 1}]
    }).json()
    resp = authed_client.put(f"/api/recipes/{recipe['id']}", json={
        "items": [{"item_id": item_b["id"], "quantity": 3}]
    })
    assert resp.status_code == 200
    ri = resp.json()["recipe_items"]
    assert len(ri) == 1
    assert ri[0]["item_id"] == item_b["id"]
    assert ri[0]["quantity"] == 3


def test_update_recipe_items_none_preserves(authed_client):
    item = authed_client.post("/api/items", json={"name": "A"}).json()
    recipe = authed_client.post("/api/recipes", json={
        "name": "R1",
        "items": [{"item_id": item["id"], "quantity": 1}]
    }).json()
    resp = authed_client.put(f"/api/recipes/{recipe['id']}", json={"name": "R1 Updated"})
    assert len(resp.json()["recipe_items"]) == 1


def test_delete_recipe(authed_client):
    recipe = authed_client.post("/api/recipes", json={"name": "R1"}).json()
    resp = authed_client.delete(f"/api/recipes/{recipe['id']}")
    assert resp.status_code == 200
    assert authed_client.get("/api/recipes").json() == []


def test_recipes_sorted_by_name(authed_client):
    authed_client.post("/api/recipes", json={"name": "Zebra"})
    authed_client.post("/api/recipes", json={"name": "Apple"})
    authed_client.post("/api/recipes", json={"name": "Mango"})
    names = [r["name"] for r in authed_client.get("/api/recipes").json()]
    assert names == ["Apple", "Mango", "Zebra"]


def test_delete_nonexistent_recipe(authed_client):
    resp = authed_client.delete("/api/recipes/9999")
    assert resp.status_code == 404


def test_update_nonexistent_recipe(authed_client):
    resp = authed_client.put("/api/recipes/9999", json={"name": "Nope"})
    assert resp.status_code == 404


def test_recipe_household_isolation(client, household, second_household, auth_headers, second_auth_headers):
    client.post("/api/recipes", json={"name": "H1 Recipe"}, headers=auth_headers)
    assert len(client.get("/api/recipes", headers=auth_headers).json()) == 1
    assert len(client.get("/api/recipes", headers=second_auth_headers).json()) == 0
