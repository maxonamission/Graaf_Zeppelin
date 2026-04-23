"""KeyVault — Encrypt/decrypt user API keys at rest.

Uses Fernet symmetric encryption with a key derived via PBKDF2-HMAC-SHA256
(S13-05). Falls back to legacy SHA-256 derivation for tokens encrypted before
the migration, so existing data keeps working without re-encryption.

Keys are never stored in plaintext or logged.
"""

from __future__ import annotations

import base64
import hashlib
import logging

from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.config import settings

_logger = logging.getLogger(__name__)

# Fixed salt so the derived key is deterministic (same secret → same key).
# This is acceptable because the secret_key already has high entropy (≥32
# chars, validated at startup) and PBKDF2 provides the key stretching that
# was missing with plain SHA-256.
_PBKDF2_SALT = b"graaf-zeppelin-keyvault-v2"
_PBKDF2_ITERATIONS = 480_000  # OWASP 2023 recommendation for HMAC-SHA256


def _derive_pbkdf2(secret: str) -> bytes:
    """Derive a 32-byte Fernet key via PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_PBKDF2_SALT,
        iterations=_PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


def _derive_legacy(secret: str) -> bytes:
    """Derive a 32-byte Fernet key via plain SHA-256 (pre-S13-05)."""
    raw = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(raw)


class KeyVault:
    """Encrypts and decrypts API keys using Fernet with the app secret.

    New encryptions use a PBKDF2-derived key (S13-05).  Decryption tries the
    PBKDF2 key first, then falls back to the legacy SHA-256 key so that
    existing ciphertext remains readable without a migration step.
    """

    def __init__(self) -> None:
        self._primary = Fernet(_derive_pbkdf2(settings.secret_key))
        self._legacy = Fernet(_derive_legacy(settings.secret_key))
        # MultiFernet tries keys in order: primary first, then legacy.
        self._multi = MultiFernet([self._primary, self._legacy])

    def encrypt(self, plaintext: str) -> str:
        """Encrypt an API key with the PBKDF2-derived key."""
        return self._primary.encrypt(plaintext.encode()).decode()

    def decrypt(self, token: str) -> str:
        """Decrypt an API key token (tries PBKDF2 key, then legacy)."""
        return self._multi.decrypt(token.encode()).decode()
