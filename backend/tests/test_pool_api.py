from datetime import datetime, timedelta
from app.models import Item, ShoppingSession, SessionItem


def test_pool_empty(authed_client):
    resp = authed_client.get("/api/pool")
    assert resp.status_code == 200
    assert resp.json() == []


def test_pool_excludes_never_checked(authed_client):
    authed_client.post("/api/items", json={"name": "Milk"})
    resp = authed_client.get("/api/pool")
    assert resp.json() == []


def test_pool_includes_checked_items(authed_client):
    item = authed_client.post("/api/items", json={"name": "Milk"}).json()
    authed_client.post("/api/list/add", json={"items": [{"item_id": item["id"], "quantity": 1}]})
    session = authed_client.post("/api/session/start").json()
    si_id = session["session_items"][0]["id"]
    authed_client.put(f"/api/session/check/{si_id}")
    authed_client.post("/api/session/complete")

    pool = authed_client.get("/api/pool").json()
    assert len(pool) == 1
    assert pool[0]["item"]["id"] == item["id"]
    assert pool[0]["frequency"] == 1


def test_pool_frequency_score_capped(authed_client, db_session, household):
    """Frequency score = min(frequency/10, 1.0) — capped at 1.0."""
    item = Item(name="Milk", household_id=household.id)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    now = datetime.utcnow()
    # Create 15 checked session items
    for i in range(15):
        s = ShoppingSession(household_id=household.id, completed_at=now)
        db_session.add(s)
        db_session.commit()
        db_session.refresh(s)
        si = SessionItem(session_id=s.id, item_id=item.id, item_name="Milk",
                         checked=True, checked_at=now - timedelta(days=60))
        db_session.add(si)
    db_session.commit()

    pool = authed_client.get("/api/pool").json()
    assert len(pool) == 1
    # freq=15, freq_score = min(15/10, 1.0) = 1.0
    # recency outside 30 days → 0
    # score = 0.4*0 + 0.6*1.0 = 0.6
    assert abs(pool[0]["score"] - 0.6) < 0.01


def test_pool_recency_score(authed_client, db_session, household):
    """Recency score = (30 - days_ago) / 30 for items within 30 days."""
    item = Item(name="Milk", household_id=household.id)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    now = datetime.utcnow()
    checked_at = now - timedelta(days=10)
    s = ShoppingSession(household_id=household.id, completed_at=now)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    si = SessionItem(session_id=s.id, item_id=item.id, item_name="Milk",
                     checked=True, checked_at=checked_at)
    db_session.add(si)
    db_session.commit()

    pool = authed_client.get("/api/pool").json()
    assert len(pool) == 1
    # recency = (30 - 10) / 30 ≈ 0.667
    # freq = 1, freq_score = 0.1
    # score = 0.4*0.667 + 0.6*0.1 ≈ 0.327
    assert pool[0]["score"] > 0.2


def test_pool_outside_30_day_window_zero_recency(authed_client, db_session, household):
    item = Item(name="Milk", household_id=household.id)
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)

    now = datetime.utcnow()
    s = ShoppingSession(household_id=household.id, completed_at=now)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)
    si = SessionItem(session_id=s.id, item_id=item.id, item_name="Milk",
                     checked=True, checked_at=now - timedelta(days=60))
    db_session.add(si)
    db_session.commit()

    pool = authed_client.get("/api/pool").json()
    # freq=1, freq_score=0.1, recency=0 → score = 0.06
    assert abs(pool[0]["score"] - 0.06) < 0.01


def test_pool_sorted_desc(authed_client, db_session, household):
    """Higher score items come first."""
    item_a = Item(name="A", household_id=household.id)
    item_b = Item(name="B", household_id=household.id)
    db_session.add_all([item_a, item_b])
    db_session.commit()
    db_session.refresh(item_a)
    db_session.refresh(item_b)

    now = datetime.utcnow()
    # A: 1 check old, B: 5 checks recent
    s = ShoppingSession(household_id=household.id, completed_at=now)
    db_session.add(s)
    db_session.commit()
    db_session.refresh(s)

    db_session.add(SessionItem(session_id=s.id, item_id=item_a.id, item_name="A",
                               checked=True, checked_at=now - timedelta(days=60)))
    for _ in range(5):
        s2 = ShoppingSession(household_id=household.id, completed_at=now)
        db_session.add(s2)
        db_session.commit()
        db_session.refresh(s2)
        db_session.add(SessionItem(session_id=s2.id, item_id=item_b.id, item_name="B",
                                   checked=True, checked_at=now - timedelta(days=2)))
    db_session.commit()

    pool = authed_client.get("/api/pool").json()
    assert len(pool) == 2
    assert pool[0]["item"]["name"] == "B"


def test_pool_max_50(authed_client, db_session, household):
    now = datetime.utcnow()
    for i in range(60):
        item = Item(name=f"Item{i}", household_id=household.id)
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        s = ShoppingSession(household_id=household.id, completed_at=now)
        db_session.add(s)
        db_session.commit()
        db_session.refresh(s)
        db_session.add(SessionItem(session_id=s.id, item_id=item.id, item_name=f"Item{i}",
                                   checked=True, checked_at=now))
    db_session.commit()

    pool = authed_client.get("/api/pool").json()
    assert len(pool) == 50


def test_pool_household_isolation(client, household, second_household, auth_headers, second_auth_headers):
    item = client.post("/api/items", json={"name": "Milk"}, headers=auth_headers).json()
    client.post("/api/list/add", json={"items": [{"item_id": item["id"], "quantity": 1}]}, headers=auth_headers)
    session = client.post("/api/session/start", headers=auth_headers).json()
    si_id = session["session_items"][0]["id"]
    client.put(f"/api/session/check/{si_id}", headers=auth_headers)
    client.post("/api/session/complete", headers=auth_headers)

    assert len(client.get("/api/pool", headers=auth_headers).json()) == 1
    assert len(client.get("/api/pool", headers=second_auth_headers).json()) == 0
