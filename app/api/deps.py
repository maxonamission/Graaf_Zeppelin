"""Shared API dependencies — current user, license validation."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.db import get_db
from app.models.user import User


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract current user from JWT cookie."""
    if not access_token:
        raise HTTPException(status_code=401, detail="Niet ingelogd")

    payload = decode_access_token(access_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Sessie verlopen")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Ongeldige sessie")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Gebruiker niet gevonden")

    return user
