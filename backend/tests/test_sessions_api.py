def _setup_list(client):
    """Helper: create items and add to list, return item IDs."""
    a = client.post("/api/items", json={"name": "Milk"}).json()
    b = client.post("/api/items", json={"name": "Bread"}).json()
    client.post("/api/list/add", json={"items": [
        {"item_id": a["id"], "quantity": 2},
        {"item_id": b["id"], "quantity": 1},
    ]})
    return a, b


def test_start_session_creates_snapshot(authed_client):
    _setup_list(authed_client)
    resp = authed_client.post("/api/session/start")
    assert resp.status_code == 200
    session = resp.json()
    assert len(session["session_items"]) == 2
    assert session["completed_at"] is None


def test_start_session_stores_item_name(authed_client):
    a, _ = _setup_list(authed_client)
    session = authed_client.post("/api/session/start").json()
    names = {si["item_name"] for si in session["session_items"]}
    assert "Milk" in names


def test_start_session_idempotent(authed_client):
    _setup_list(authed_client)
    s1 = authed_client.post("/api/session/start").json()
    s2 = authed_client.post("/api/session/start").json()
    assert s1["id"] == s2["id"]


def test_get_active_session(authed_client):
    _setup_list(authed_client)
    authed_client.post("/api/session/start")
    resp = authed_client.get("/api/session/active")
    assert resp.status_code == 200
    assert resp.json() is not None


def test_get_active_session_null(authed_client):
    resp = authed_client.get("/api/session/active")
    assert resp.status_code == 200
    assert resp.json() is None


def test_toggle_check_on(authed_client):
    _setup_list(authed_client)
    session = authed_client.post("/api/session/start").json()
    si_id = session["session_items"][0]["id"]
    resp = authed_client.put(f"/api/session/check/{si_id}")
    assert resp.status_code == 200
    assert resp.json()["checked"] is True
    assert resp.json()["checked_at"] is not None


def test_toggle_check_off(authed_client):
    _setup_list(authed_client)
    session = authed_client.post("/api/session/start").json()
    si_id = session["session_items"][0]["id"]
    authed_client.put(f"/api/session/check/{si_id}")  # on
    resp = authed_client.put(f"/api/session/check/{si_id}")  # off
    assert resp.json()["checked"] is False
    assert resp.json()["checked_at"] is None


def test_toggle_check_404(authed_client):
    resp = authed_client.put("/api/session/check/9999")
    assert resp.status_code == 404


def test_complete_session_sets_completed_at(authed_client):
    _setup_list(authed_client)
    authed_client.post("/api/session/start")
    resp = authed_client.post("/api/session/complete")
    assert resp.status_code == 200
    assert resp.json()["completed_at"] is not None


def test_complete_session_deletes_checked_items(authed_client):
    a, b = _setup_list(authed_client)
    session = authed_client.post("/api/session/start").json()
    # Check the first item
    milk_si = next(si for si in session["session_items"] if si["item_name"] == "Milk")
    authed_client.put(f"/api/session/check/{milk_si['id']}")
    authed_client.post("/api/session/complete")
    list_items = authed_client.get("/api/list").json()
    item_ids = [li["item_id"] for li in list_items]
    assert a["id"] not in item_ids  # Milk was checked → removed
    assert b["id"] in item_ids  # Bread unchecked → kept


def test_complete_session_keeps_unchecked(authed_client):
    _setup_list(authed_client)
    authed_client.post("/api/session/start")
    authed_client.post("/api/session/complete")
    # Nothing was checked, so everything stays
    assert len(authed_client.get("/api/list").json()) == 2


def test_complete_no_active_session(authed_client):
    resp = authed_client.post("/api/session/complete")
    assert resp.status_code == 404


def test_abort_session_deletes_session(authed_client):
    _setup_list(authed_client)
    authed_client.post("/api/session/start")
    resp = authed_client.delete("/api/session/active")
    assert resp.status_code == 200
    assert authed_client.get("/api/session/active").json() is None


def test_abort_session_leaves_list_intact(authed_client):
    _setup_list(authed_client)
    authed_client.post("/api/session/start")
    authed_client.delete("/api/session/active")
    assert len(authed_client.get("/api/list").json()) == 2


def test_abort_no_active_session(authed_client):
    resp = authed_client.delete("/api/session/active")
    assert resp.status_code == 404


def test_list_completed_sessions_ordered_desc(authed_client):
    a = authed_client.post("/api/items", json={"name": "X"}).json()
    authed_client.post("/api/list/add", json={"items": [{"item_id": a["id"], "quantity": 1}]})

    authed_client.post("/api/session/start")
    authed_client.post("/api/session/complete")

    # Second session
    authed_client.post("/api/list/add", json={"items": [{"item_id": a["id"], "quantity": 1}]})
    authed_client.post("/api/session/start")
    authed_client.post("/api/session/complete")

    sessions = authed_client.get("/api/sessions").json()
    assert len(sessions) == 2
    assert sessions[0]["completed_at"] >= sessions[1]["completed_at"]


def test_delete_past_session(authed_client):
    a = authed_client.post("/api/items", json={"name": "X"}).json()
    authed_client.post("/api/list/add", json={"items": [{"item_id": a["id"], "quantity": 1}]})
    authed_client.post("/api/session/start")
    authed_client.post("/api/session/complete")
    sessions = authed_client.get("/api/sessions").json()
    resp = authed_client.delete(f"/api/sessions/{sessions[0]['id']}")
    assert resp.status_code == 200
    assert authed_client.get("/api/sessions").json() == []
