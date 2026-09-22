from datetime import timedelta, datetime, timezone
from jose import jwt

from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)


def test_password_roundtrip():
    stored = hash_password("secret")
    assert stored.startswith("pbkdf2_sha256$")
    assert verify_password("secret", stored)
    assert not verify_password("Secret", stored)


def test_password_hash_is_salted():
    assert hash_password("secret") != hash_password("secret")


def test_empty_stored_hash_matches_only_empty_password():
    assert verify_password("", "")
    assert not verify_password("secret", "")


def test_malformed_stored_hash_rejected():
    assert not verify_password("secret", "garbage")


def test_jwt_contains_sub():
    token = create_access_token(data={"sub": "42"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "42"


def test_jwt_contains_exp():
    token = create_access_token(data={"sub": "1"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload


def test_jwt_custom_expiry():
    token = create_access_token(data={"sub": "1"}, expires_delta=timedelta(minutes=5))
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    assert (exp - now).total_seconds() < 310  # ~5 min + tolerance


def test_jwt_invalid_token():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid.jwt.token"})
        assert resp.status_code == 401


def test_jwt_missing_token():
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as client:
        resp = client.get("/api/auth/me")
        assert resp.status_code in (401, 403)  # HTTPBearer may return either
