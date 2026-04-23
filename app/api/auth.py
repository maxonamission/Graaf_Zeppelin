"""Authentication API — login, registration, and session management."""

from __future__ import annotations

import json as _json
import logging
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.audit import audit_log
from app.core.auth import (
    REFRESH_TOKEN_DAYS,
    create_access_token,
    create_refresh_token,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.core.license_manager import LicenseManager
from app.core.rate_limit import limiter
from app.db import get_db
from app.models.refresh_token import RefreshToken
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _set_token_cookie(response: Response, token: str) -> None:
    """Set access_token as a secure, httponly cookie."""
    is_prod = settings.environment == "production"
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    """Set refresh_token as a secure, httponly cookie (S11-01)."""
    is_prod = settings.environment == "production"
    response.set_cookie(
        key="refresh_token",
        value=raw_token,
        httponly=True,
        secure=is_prod,
        samesite="lax",
        max_age=REFRESH_TOKEN_DAYS * 86400,
        path="/api/auth/refresh",
    )


def _validate_password_complexity(password: str) -> str:
    """Enforce password complexity: min 12 chars, mix of upper/lower/digits (S11-01)."""
    if len(password) < 12:
        raise ValueError("Wachtwoord moet minimaal 12 tekens bevatten")
    if not any(c.isupper() for c in password):
        raise ValueError("Wachtwoord moet minimaal één hoofdletter bevatten")
    if not any(c.islower() for c in password):
        raise ValueError("Wachtwoord moet minimaal één kleine letter bevatten")
    if not any(c.isdigit() for c in password):
        raise ValueError("Wachtwoord moet minimaal één cijfer bevatten")
    return password


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Wachtwoord moet minimaal 12 tekens bevatten met hoofdletters, kleine letters en cijfers",
    )
    full_name: str = Field(..., min_length=1, max_length=200)
    organization: str = Field(..., min_length=1, max_length=200)
    license_key: str

    @field_validator("password")
    @classmethod
    def check_password_complexity(cls, v: str) -> str:
        return _validate_password_complexity(v)


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=320)
    password: str = Field(..., max_length=128)


async def _issue_tokens(user: User, db: AsyncSession, response: Response) -> None:
    """Issue access + refresh tokens and set cookies (S11-01)."""
    access_token = create_access_token({"sub": user.email})
    _set_token_cookie(response, access_token)

    raw_refresh, token_hash = create_refresh_token()
    rt = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_DAYS),
    )
    db.add(rt)
    await db.commit()
    _set_refresh_cookie(response, raw_refresh)


@router.post("/register")
@limiter.limit("3/hour")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):

    # Verify license
    lm = LicenseManager(db)
    try:
        await lm.validate_license(data.license_key)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Ongeldige licentie") from exc

    # Check user limit for license
    if not await lm.check_user_count(data.license_key):
        raise HTTPException(
            status_code=400,
            detail="Maximaal aantal gebruikers voor deze licentie bereikt",
        )

    # Check if email exists — use generic message to prevent account enumeration
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Registratie niet mogelijk met deze gegevens",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        organization=data.organization,
        license_key=data.license_key,
    )
    db.add(user)
    await db.commit()

    audit_log(
        "user_registered",
        user_id=user.id,
        ip=request.client.host if request.client else None,
    )

    response = Response(
        content='{"token_type":"bearer","needs_onboarding":true}',
        media_type="application/json",
    )
    await _issue_tokens(user, db, response)
    return response


@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    client_ip = request.client.host if request.client else None
    if not user or not verify_password(data.password, user.hashed_password):
        audit_log("login_failed", ip=client_ip, detail=data.email)
        raise HTTPException(status_code=401, detail="Ongeldige inloggegevens")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is gedeactiveerd")

    # S11-01: Rehash legacy HMAC-SHA256 passwords to bcrypt on successful login
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(data.password)
        await db.commit()
        logger.info("Rehashed legacy password to bcrypt for user %s", user.id)

    # Validate license on every login
    if user.license_key:
        lm = LicenseManager(db)
        try:
            await lm.validate_license(user.license_key)
        except Exception as exc:
            audit_log("license_validation_failed", user_id=user.id, ip=client_ip)
            raise HTTPException(status_code=403, detail="Licentieprobleem") from exc

    audit_log("login_success", user_id=user.id, ip=client_ip)

    body = _json.dumps(
        {
            "token_type": "bearer",
            "needs_onboarding": not user.has_completed_onboarding,
        }
    )
    response = Response(content=body, media_type="application/json")
    await _issue_tokens(user, db, response)
    return response


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(None),
):
    """Exchange a valid refresh token for a new access + refresh token pair (S11-01).

    Implements refresh-token rotation: the old token is invalidated and a new pair is issued.
    """
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Geen refresh token")

    import hashlib

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()

    if not stored or stored.expires_at < datetime.now(UTC):
        if stored:
            # Possible token reuse — revoke all tokens for this user
            await db.execute(delete(RefreshToken).where(RefreshToken.user_id == stored.user_id))
            await db.commit()
            logger.warning("Refresh token reuse detected for user %s", stored.user_id)
        raise HTTPException(status_code=401, detail="Ongeldige of verlopen refresh token")

    # Load user
    user_result = await db.execute(select(User).where(User.id == stored.user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account niet gevonden of gedeactiveerd")

    # Rotate: delete old token, issue new pair
    await db.delete(stored)

    body = _json.dumps({"token_type": "bearer"})
    response = Response(content=body, media_type="application/json")
    await _issue_tokens(user, db, response)

    audit_log(
        "token_refreshed", user_id=user.id, ip=request.client.host if request.client else None
    )

    return response


@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(None),
):
    """Clear access + refresh token cookies and revoke the refresh token."""
    if refresh_token:
        import hashlib

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        await db.execute(delete(RefreshToken).where(RefreshToken.token_hash == token_hash))
        await db.commit()

    response = Response(content='{"logged_out":true}', media_type="application/json")
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/api/auth/refresh")
    return response


@router.post("/onboarding/complete")
async def complete_onboarding(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark the onboarding flow as completed for the current user."""
    user.has_completed_onboarding = True
    await db.commit()
    return {"completed": True}


@router.get("/onboarding/status")
async def onboarding_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check if the current user needs onboarding."""
    return {"needs_onboarding": not user.has_completed_onboarding}
