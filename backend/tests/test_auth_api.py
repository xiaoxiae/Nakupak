def test_create_household(client):
    resp = client.post("/api/auth/create")
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_join_household(client, household):
    resp = client.post("/api/auth/join", json={"token": household.token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_join_case_insensitive(client, household):
    resp = client.post("/api/auth/join", json={"token": household.token.lower()})
    assert resp.status_code == 200


def test_join_whitespace_handling(client, household):
    resp = client.post("/api/auth/join", json={"token": f"  {household.token}  "})
    assert resp.status_code == 200


def test_join_invalid_token(client):
    resp = client.post("/api/auth/join", json={"token": "ZZZZ-ZZZZ"})
    assert resp.status_code == 404


def test_me_authenticated(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert "created_at" in data


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code in (401, 403)


def test_create_then_join_roundtrip(client):
    create_resp = client.post("/api/auth/create")
    token = create_resp.json()["access_token"]
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    household_token = me_resp.json()["token"]
    join_resp = client.post("/api/auth/join", json={"token": household_token})
    assert join_resp.status_code == 200
