"""Authentication API — login, registration, and session management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.license_manager import LicenseManager
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organization: str
    license_key: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Verify license
    lm = LicenseManager(db)
    try:
        await lm.validate_license(data.license_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Ongeldige inloggegevens")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is gedeactiveerd")

    # Validate license on every login
    if user.license_key:
        lm = LicenseManager(db)
        try:
            await lm.validate_license(user.license_key)
        except Exception as e:
            raise HTTPException(status_code=403, detail=f"Licentieprobleem: {e}")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
