"""Authentication API — login, registration, and session management."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.audit import audit_log
from app.core.auth import create_access_token, hash_password, verify_password


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
from app.core.license_manager import LicenseManager
from app.db import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=12,
        max_length=128,
        description="Wachtwoord moet minimaal 12 tekens bevatten",
    )
    full_name: str = Field(..., min_length=1, max_length=200)
    organization: str = Field(..., min_length=1, max_length=200)
    license_key: str


class LoginRequest(BaseModel):
    email: str = Field(..., max_length=320)
    password: str = Field(..., max_length=128)


@router.post("/register")
async def register(request: Request, data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    await request.app.state.limiter.check("5/minute", request)

    # Verify license
    lm = LicenseManager(db)
    try:
        await lm.validate_license(data.license_key)
    except Exception:
        raise HTTPException(status_code=400, detail="Ongeldige licentie")

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

    token = create_access_token({"sub": user.email})
    response = Response(
        content='{"token_type":"bearer","needs_onboarding":true}',
        media_type="application/json",
    )
    _set_token_cookie(response, token)
    return response


@router.post("/login")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    await request.app.state.limiter.check("10/minute", request)

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    client_ip = request.client.host if request.client else None
    if not user or not verify_password(data.password, user.hashed_password):
        audit_log("login_failed", ip=client_ip, detail=data.email)
        raise HTTPException(status_code=401, detail="Ongeldige inloggegevens")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is gedeactiveerd")

    # Validate license on every login
    if user.license_key:
        lm = LicenseManager(db)
        try:
            await lm.validate_license(user.license_key)
        except Exception:
            logger.warning("Licentievalidatie mislukt voor gebruiker %s", user.id)
            raise HTTPException(status_code=403, detail="Licentieprobleem")

    audit_log("login_success", user_id=user.id, ip=client_ip)

    import json as _json

    token = create_access_token({"sub": user.email})
    body = _json.dumps({
        "token_type": "bearer",
        "needs_onboarding": not user.has_completed_onboarding,
    })
    response = Response(content=body, media_type="application/json")
    _set_token_cookie(response, token)
    return response


@router.post("/logout")
async def logout():
    """Clear the access_token cookie server-side."""
    response = Response(content='{"logged_out":true}', media_type="application/json")
    response.delete_cookie(key="access_token", path="/")
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
