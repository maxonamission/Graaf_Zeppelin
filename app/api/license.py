"""License API — license info, validation, free quota, and BYOK key management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.key_vault import KeyVault
from app.core.license_manager import LicenseManager
from app.db import get_db
from app.models.user import User
from app.models.user_api_key import UserApiKey

router = APIRouter(prefix="/api/license", tags=["license"])


class StoreApiKeyRequest(BaseModel):
    provider: str  # openai, anthropic
    api_key: str


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


# ── Free quota (S07-01) ──────────────────────────────────────────────


@router.get("/free-quota")
async def get_free_quota(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get daily free-question usage for the current user.

    Returns usage counters including remaining free questions today.
    Non-free-tier users get is_free_tier=False.
    """
    # Users without a license key are on free tier
    if user.license_key:
        lm = LicenseManager(db)
        try:
            license_obj = await lm.validate_license(user.license_key)
            if license_obj.tier != "free":
                return {"is_free_tier": False}
        except Exception:
            pass

    lm = LicenseManager(db)
    return await lm.get_daily_usage(user.id)


# ── BYOK key management (S07-04) ─────────────────────────────────────


@router.post("/api-keys")
async def store_api_key(
    request: StoreApiKeyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Store or update the user's own LLM API key (encrypted).

    Only available for BYOK tier users.
    The key is encrypted at rest and never exposed in logs.
    """
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")

    lm = LicenseManager(db)
    if not await lm.is_byok_tier(user.license_key):
        raise HTTPException(
            status_code=403,
            detail="API-sleutelopslag is alleen beschikbaar voor BYOK-licenties",
        )

    if request.provider not in ("openai", "anthropic"):
        raise HTTPException(status_code=422, detail="Provider moet 'openai' of 'anthropic' zijn")

    if len(request.api_key) < 10:
        raise HTTPException(status_code=422, detail="Ongeldige API-sleutel")

    vault = KeyVault()
    encrypted = vault.encrypt(request.api_key)
    hint = f"...{request.api_key[-4:]}"

    # Upsert: deactivate existing key for this provider, add new one
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.user_id == user.id,
            UserApiKey.provider == request.provider,
            UserApiKey.is_active == True,  # noqa: E712
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.is_active = False

    new_key = UserApiKey(
        user_id=user.id,
        provider=request.provider,
        encrypted_key=encrypted,
        key_hint=hint,
        is_active=True,
    )
    db.add(new_key)
    await db.commit()

    return {"provider": request.provider, "hint": hint, "stored": True}


@router.get("/api-keys")
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List stored API keys (hints only, never the actual keys)."""
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.user_id == user.id,
            UserApiKey.is_active == True,  # noqa: E712
        )
    )
    keys = result.scalars().all()
    return {
        "keys": [
            {
                "id": k.id,
                "provider": k.provider,
                "hint": k.key_hint,
                "created_at": k.created_at.isoformat(),
            }
            for k in keys
        ]
    }


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Deactivate a stored API key."""
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.id == key_id,
            UserApiKey.user_id == user.id,
        )
    )
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404, detail="API-sleutel niet gevonden")
    key.is_active = False
    await db.commit()
    return {"deleted": True}


# ── Credits top-up (S07-03) ──────────────────────────────────────────


class TopUpRequest(BaseModel):
    amount: int  # number of extra credits to add


@router.post("/credits/topup")
async def topup_credits(
    request: TopUpRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add extra credits (flexible top-up) to the user's license.

    In a real system this would involve payment processing.
    For now it directly adds credits to the license quota.
    """
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")

    if request.amount <= 0:
        raise HTTPException(status_code=422, detail="Aantal moet positief zijn")

    from app.models.license import License
    result = await db.execute(
        select(License).where(License.key == user.license_key)
    )
    license_obj = result.scalar_one_or_none()
    if not license_obj:
        raise HTTPException(status_code=404, detail="Licentie niet gevonden")

    # Reset usage counter by reducing queries_used (simulates adding credits)
    license_obj.queries_used = max(0, license_obj.queries_used - request.amount)
    await db.commit()

    lm = LicenseManager(db)
    info = await lm.get_license_info(user.license_key)

    return {
        "credits_added": request.amount,
        "queries_used": info["queries_used"],
        "queries_limit": info["queries_limit"],
    }


@router.get("/credits/status")
async def credits_status(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed credits/quota status including warning level."""
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")

    lm = LicenseManager(db)
    try:
        info = await lm.get_license_info(user.license_key)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    used = info["queries_used"]
    limit = info["queries_limit"]
    pct = (used / limit * 100) if limit > 0 else 0

    if pct >= 100:
        warning = "limit_reached"
    elif pct >= 80:
        warning = "approaching_limit"
    else:
        warning = None

    return {
        "queries_used": used,
        "queries_limit": limit,
        "percentage": round(pct, 1),
        "warning": warning,
        "tier": info["tier"],
    }
