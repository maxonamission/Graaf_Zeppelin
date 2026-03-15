"""Authentication API — login, registration, and session management."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.auth import create_access_token, hash_password, verify_password
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

    # Check if email exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="E-mailadres is al geregistreerd")

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        organization=data.organization,
        license_key=data.license_key,
    )
    db.add(user)
    await db.commit()

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer", "needs_onboarding": True}


@router.post("/login")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    await request.app.state.limiter.check("10/minute", request)

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        logger.warning("Mislukte login voor e-mail: %s", data.email)
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

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "needs_onboarding": not user.has_completed_onboarding,
    }


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
