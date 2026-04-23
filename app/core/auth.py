"""Authentication utilities — JWT tokens and password hashing.

Uses bcrypt for password hashing and stdlib for JWT (HS256).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt

from app.config import settings

ALGORITHM = "HS256"
REFRESH_TOKEN_DAYS = 7


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with cost factor 12."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash.

    Also supports legacy HMAC-SHA256 hashes (salt$hex format) for migration.
    """
    if "$2" in hashed[:4]:
        # bcrypt hash
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    # Legacy HMAC-SHA256 format: salt$hexdigest
    if "$" not in hashed:
        return False
    salt, expected = hashed.split("$", 1)
    h = hmac.new(salt.encode(), plain.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(h, expected)


def needs_rehash(hashed: str) -> bool:
    """Check if a password hash uses legacy HMAC-SHA256 and needs migration to bcrypt."""
    return "$2" not in hashed[:4]


def create_refresh_token() -> tuple[str, str]:
    """Generate a random refresh token and its SHA-256 hash.

    Returns (raw_token, token_hash). The raw token is sent to the client;
    only the hash is stored in the database.
    """
    raw = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, token_hash


def verify_refresh_token(raw: str, stored_hash: str) -> bool:
    """Verify a raw refresh token against its stored hash."""
    computed = hashlib.sha256(raw.encode()).hexdigest()
    return hmac.compare_digest(computed, stored_hash)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token using HS256."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode["exp"] = int(expire.timestamp())

    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(json.dumps(to_encode).encode())
    signing_input = f"{header}.{payload}"

    signature = hmac.new(
        settings.secret_key.encode(), signing_input.encode(), hashlib.sha256
    ).digest()
    sig_encoded = _b64url_encode(signature)

    return f"{header}.{payload}.{sig_encoded}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT access token.

    Validates the algorithm in the header is HS256 to prevent
    algorithm-confusion attacks (e.g. "alg": "none").
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_b64, payload_b64, signature_b64 = parts

        # Validate algorithm before checking signature
        header = json.loads(_b64url_decode(header_b64))
        if header.get("alg") != ALGORITHM:
            return None

        signing_input = f"{header_b64}.{payload_b64}"

        expected_sig = hmac.new(
            settings.secret_key.encode(), signing_input.encode(), hashlib.sha256
        ).digest()
        actual_sig = _b64url_decode(signature_b64)

        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload = json.loads(_b64url_decode(payload_b64))
        if not isinstance(payload, dict):
            return None

        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.now(UTC).timestamp() > exp:
            return None

        return payload
    except Exception:
        return None
