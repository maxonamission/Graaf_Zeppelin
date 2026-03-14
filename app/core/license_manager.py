"""
License Manager — Validates and manages user licenses.

Licenses are tied to organizations and checked on every session.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from enum import Enum

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.license import License
from app.models.user import User


class LicenseTier(str, Enum):
    BASIS = "basis"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


TIER_LIMITS = {
    LicenseTier.BASIS: {"queries_per_month": 100, "users": 3},
    LicenseTier.PROFESSIONAL: {"queries_per_month": 1000, "users": 15},
    LicenseTier.ENTERPRISE: {"queries_per_month": 10000, "users": 100},
}


class LicenseError(Exception):
    """Raised when a license check fails."""


class LicenseManager:
    """Manages license creation, validation, and enforcement."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_license(
        self,
        organization: str,
        tier: LicenseTier,
        valid_days: int = 365,
    ) -> License:
        """Create a new license for an organization."""
        license_key = self._generate_key()
        now = datetime.now(timezone.utc)

        license_obj = License(
            key=license_key,
            organization=organization,
            tier=tier.value,
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(days=valid_days),
            queries_used=0,
        )
        self.db.add(license_obj)
        await self.db.commit()
        await self.db.refresh(license_obj)
        return license_obj

    async def validate_license(self, license_key: str) -> License:
        """Validate a license key and return the license if valid."""
        result = await self.db.execute(
            select(License).where(License.key == license_key)
        )
        license_obj = result.scalar_one_or_none()

        if not license_obj:
            raise LicenseError("Ongeldige licentiesleutel")

        if not license_obj.is_active:
            raise LicenseError("Licentie is gedeactiveerd")

        now = datetime.now(timezone.utc)
        expires_at = license_obj.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            raise LicenseError("Licentie is verlopen")

        limits = TIER_LIMITS.get(LicenseTier(license_obj.tier))
        if limits and license_obj.queries_used >= limits["queries_per_month"]:
            raise LicenseError("Maandelijks querylimiet bereikt")

        return license_obj

    async def record_query(self, license_key: str) -> None:
        """Record a query against a license's usage counter."""
        result = await self.db.execute(
            select(License).where(License.key == license_key)
        )
        license_obj = result.scalar_one_or_none()
        if license_obj:
            license_obj.queries_used += 1
            await self.db.commit()

    async def get_license_info(self, license_key: str) -> dict:
        """Get detailed license information."""
        license_obj = await self.validate_license(license_key)
        tier = LicenseTier(license_obj.tier)
        limits = TIER_LIMITS[tier]

        return {
            "organization": license_obj.organization,
            "tier": license_obj.tier,
            "is_active": license_obj.is_active,
            "created_at": license_obj.created_at.isoformat(),
            "expires_at": license_obj.expires_at.isoformat(),
            "queries_used": license_obj.queries_used,
            "queries_limit": limits["queries_per_month"],
            "users_limit": limits["users"],
        }

    async def check_user_count(self, license_key: str) -> bool:
        """Check if the license can accommodate another user."""
        license_obj = await self.validate_license(license_key)
        tier = LicenseTier(license_obj.tier)
        limits = TIER_LIMITS[tier]

        result = await self.db.execute(
            select(User).where(User.license_key == license_key)
        )
        current_users = len(result.scalars().all())
        return current_users < limits["users"]

    @staticmethod
    def _generate_key() -> str:
        """Generate a unique license key."""
        return f"GZ-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}"
