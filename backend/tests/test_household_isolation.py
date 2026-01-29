"""Cross-household isolation: data from one household must not leak to another."""


def _create_full_setup(client, headers):
    """Create items, categories, recipes, list entries, and a session for a household."""
    cat = client.post("/api/categories", json={"name": "Cat"}, headers=headers).json()
    item = client.post("/api/items", json={"name": "Item", "category_id": cat["id"]}, headers=headers).json()
    client.post("/api/recipes", json={"name": "Recipe", "items": [{"item_id": item["id"], "quantity": 1}]}, headers=headers)
    client.post("/api/list/add", json={"items": [{"item_id": item["id"], "quantity": 1}]}, headers=headers)
    client.post("/api/session/start", headers=headers)
    return item


def test_items_isolation(client, household, second_household, auth_headers, second_auth_headers):
    client.post("/api/items", json={"name": "H1 Item"}, headers=auth_headers)
    assert len(client.get("/api/items", headers=auth_headers).json()) == 1
    assert len(client.get("/api/items", headers=second_auth_headers).json()) == 0


def test_list_isolation(client, household, second_household, auth_headers, second_auth_headers):
    item = client.post("/api/items", json={"name": "H1 Item"}, headers=auth_headers).json()
    client.post("/api/list/add", json={"items": [{"item_id": item["id"], "quantity": 1}]}, headers=auth_headers)
    assert len(client.get("/api/list", headers=auth_headers).json()) == 1
    assert len(client.get("/api/list", headers=second_auth_headers).json()) == 0


def test_sessions_isolation(client, household, second_household, auth_headers, second_auth_headers):
    item = client.post("/api/items", json={"name": "H1"}, headers=auth_headers).json()
    client.post("/api/list/add", json={"items": [{"item_id": item["id"], "quantity": 1}]}, headers=auth_headers)
    client.post("/api/session/start", headers=auth_headers)

    active1 = client.get("/api/session/active", headers=auth_headers).json()
    active2 = client.get("/api/session/active", headers=second_auth_headers).json()
    assert active1 is not None
    assert active2 is None


def test_recipes_isolation(client, household, second_household, auth_headers, second_auth_headers):
    client.post("/api/recipes", json={"name": "H1 Recipe"}, headers=auth_headers)
    assert len(client.get("/api/recipes", headers=auth_headers).json()) == 1
    assert len(client.get("/api/recipes", headers=second_auth_headers).json()) == 0


def test_categories_isolation(client, household, second_household, auth_headers, second_auth_headers):
    client.post("/api/categories", json={"name": "H1 Cat"}, headers=auth_headers)
    assert len(client.get("/api/categories", headers=auth_headers).json()) == 1
    assert len(client.get("/api/categories", headers=second_auth_headers).json()) == 0
