"""KeyVault — Encrypt/decrypt user API keys at rest.

Uses Fernet symmetric encryption derived from the app's secret_key.
Keys are never stored in plaintext or logged.
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.config import settings


class KeyVault:
    """Encrypts and decrypts API keys using Fernet with the app secret."""

    def __init__(self) -> None:
        # Derive a 32-byte key from the app secret
        raw = hashlib.sha256(settings.secret_key.encode()).digest()
        self._fernet = Fernet(base64.urlsafe_b64encode(raw))

    def encrypt(self, plaintext: str) -> str:
        """Encrypt an API key and return a base64 token."""
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Decrypt an encrypted API key token."""
        return self._fernet.decrypt(token.encode()).decode()
