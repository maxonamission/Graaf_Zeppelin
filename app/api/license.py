"""License API — license info and validation."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.license_manager import LicenseManager
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/license", tags=["license"])


@router.get("/info")
async def license_info(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get license details for the current user."""
    if not user.license_key:
        raise HTTPException(status_code=404, detail="Geen licentie gekoppeld")

    lm = LicenseManager(db)
    try:
        info = await lm.get_license_info(user.license_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return info


@router.get("/validate")
async def validate_license(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Quick license validation check."""
    if not user.license_key:
        return {"valid": False, "reason": "Geen licentie gekoppeld"}

    lm = LicenseManager(db)
    try:
        await lm.validate_license(user.license_key)
        return {"valid": True}
    except Exception as e:
        return {"valid": False, "reason": str(e)}
