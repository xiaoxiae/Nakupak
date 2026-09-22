from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import base64
import hashlib
import hmac
from sqlalchemy.orm import Session
import os

from .database import get_db
from .models import Household
from .schemas import TokenData

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

bearer_scheme = HTTPBearer()


PBKDF2_ITERATIONS = 600_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITERATIONS)
    return "$".join([
        "pbkdf2_sha256",
        str(PBKDF2_ITERATIONS),
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    ])


def verify_password(password: str, stored: str) -> bool:
    # Households migrated from the old code-only login have an empty hash,
    # which means an empty password until one is set in settings.
    if stored == "":
        return password == ""
    try:
        algorithm, iterations, salt, digest = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(iterations))
    return hmac.compare_digest(candidate, base64.b64decode(digest))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_household(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    db: Session = Depends(get_db)
) -> Household:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        household_id_str = payload.get("sub")
        if household_id_str is None:
            raise credentials_exception
        token_data = TokenData(household_id=int(household_id_str))
    except JWTError:
        raise credentials_exception

    household = db.query(Household).filter(Household.id == token_data.household_id).first()
    if household is None:
        raise credentials_exception
    return household


def get_household_from_jwt(token: str, db: Session) -> Household | None:
    """Decode a JWT string and return the Household, or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        household_id_str = payload.get("sub")
        if household_id_str is None:
            return None
        household = db.query(Household).filter(Household.id == int(household_id_str)).first()
        return household
    except JWTError:
        return None
