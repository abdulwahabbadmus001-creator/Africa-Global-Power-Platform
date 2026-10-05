from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)


def create_access_token(
    subject: str,
    *,
    minutes: int | None = None,
    auth_level: str = "standard",
) -> str:
    lifetime = minutes if minutes is not None else settings.access_token_minutes
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=lifetime)
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": now,
        "type": "access",
        "auth_level": auth_level,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_claims(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
        if payload.get("type") != "access":
            return None
        if not payload.get("sub"):
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_access_token(token: str) -> str | None:
    payload = decode_access_claims(token)
    if not payload:
        return None
    return payload.get("sub")


def create_purpose_token(
    subject: str,
    *,
    purpose: str,
    minutes: int,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=minutes)
    payload = {
        "sub": subject,
        "purpose": purpose,
        "type": "challenge",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_purpose_token(token: str, *, purpose: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[ALGORITHM],
        )
        if payload.get("type") != "challenge":
            return None
        if payload.get("purpose") != purpose:
            return None
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
