import re
from datetime import timedelta, datetime, timezone
from jose import jwt

from app.auth import (
    generate_household_token,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)


def test_token_format():
    token = generate_household_token()
    assert re.match(r"^[0-9A-F]{4}-[0-9A-F]{4}$", token)


def test_token_checksum():
    for _ in range(20):
        token = generate_household_token()
        digits = token.replace("-", "")
        digit_sum = sum(int(c, 16) for c in digits)
        assert digit_sum % 4 == 0


def test_token_uniqueness():
    tokens = {generate_household_token() for _ in range(50)}
    # With 8 hex digits, collisions in 50 samples are extremely unlikely
    assert len(tokens) >= 45


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
