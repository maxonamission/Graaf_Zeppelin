"""Tests for the auth module — JWT tokens and password hashing."""

import time

from app.core.auth import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "secure-password-123"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct-password")
        assert not verify_password("wrong-password", hashed)

    def test_hash_is_bcrypt(self):
        hashed = hash_password("TestPassword1")
        # bcrypt hashes start with $2b$ (or $2a$/$2y$)
        assert hashed.startswith("$2"), f"Expected bcrypt hash, got: {hashed[:10]}"
        # bcrypt format: $2b$rounds$22-char-salt+31-char-hash
        assert len(hashed) == 60

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same-password")
        h2 = hash_password("same-password")
        assert h1 != h2  # different salts

    def test_empty_password(self):
        hashed = hash_password("")
        assert verify_password("", hashed)
        assert not verify_password("notempty", hashed)


class TestJWT:
    def test_create_and_decode(self):
        data = {"sub": "user@example.com", "role": "admin"}
        token = create_access_token(data)
        decoded = decode_access_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user@example.com"
        assert decoded["role"] == "admin"
        assert "exp" in decoded

    def test_expired_token_returns_none(self):
        from datetime import timedelta

        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(seconds=-1),
        )
        assert decode_access_token(token) is None

    def test_tampered_token_returns_none(self):
        token = create_access_token({"sub": "user@example.com"})
        # Tamper with the payload
        parts = token.split(".")
        parts[1] = parts[1] + "x"
        tampered = ".".join(parts)
        assert decode_access_token(tampered) is None

    def test_invalid_format_returns_none(self):
        assert decode_access_token("not-a-jwt") is None
        assert decode_access_token("a.b") is None
        assert decode_access_token("") is None

    def test_custom_expiration(self):
        from datetime import timedelta

        token = create_access_token(
            {"sub": "user@example.com"},
            expires_delta=timedelta(hours=2),
        )
        decoded = decode_access_token(token)
        assert decoded is not None
        # Should expire ~2 hours from now
        assert decoded["exp"] > time.time()
        assert decoded["exp"] < time.time() + 7201
