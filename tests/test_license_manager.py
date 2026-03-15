"""Tests for the LicenseManager — license creation, validation, and quota enforcement."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.license_manager import (
    TIER_LIMITS,
    LicenseError,
    LicenseManager,
    LicenseTier,
)
from app.models.base import Base
from app.models.license import License
from app.models.user import User


@pytest.fixture
async def db_session():
    """Create a fresh in-memory database for each test."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


class TestLicenseTiers:
    def test_tier_enum_values(self):
        assert LicenseTier.BASIS.value == "basis"
        assert LicenseTier.PROFESSIONAL.value == "professional"
        assert LicenseTier.ENTERPRISE.value == "enterprise"

    def test_tier_limits_exist(self):
        for tier in LicenseTier:
            assert tier in TIER_LIMITS
            assert "queries_per_month" in TIER_LIMITS[tier]
            assert "users" in TIER_LIMITS[tier]

    def test_tier_limits_values(self):
        assert TIER_LIMITS[LicenseTier.BASIS]["queries_per_month"] == 100
        assert TIER_LIMITS[LicenseTier.PROFESSIONAL]["queries_per_month"] == 1000
        assert TIER_LIMITS[LicenseTier.ENTERPRISE]["queries_per_month"] == 10000


@pytest.mark.asyncio
class TestLicenseCreation:
    async def test_create_license(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Test Org", LicenseTier.BASIS)
        assert lic.organization == "Test Org"
        assert lic.tier == "basis"
        assert lic.is_active is True
        assert lic.queries_used == 0
        assert lic.key.startswith("GZ-")

    async def test_create_license_custom_days(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Test Org", LicenseTier.PROFESSIONAL, valid_days=30)
        delta = lic.expires_at - lic.created_at
        assert 29 <= delta.days <= 30

    async def test_license_key_format(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        # Format: GZ-XXXXXXXX-XXXXXXXX
        parts = lic.key.split("-")
        assert parts[0] == "GZ"
        assert len(parts) == 3


@pytest.mark.asyncio
class TestLicenseValidation:
    async def test_validate_valid_license(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        result = await lm.validate_license(lic.key)
        assert result.key == lic.key

    async def test_validate_invalid_key(self, db_session):
        lm = LicenseManager(db_session)
        with pytest.raises(LicenseError, match="Ongeldige licentiesleutel"):
            await lm.validate_license("INVALID-KEY")

    async def test_validate_inactive_license(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        # Deactivate
        lic.is_active = False
        await db_session.commit()

        with pytest.raises(LicenseError, match="gedeactiveerd"):
            await lm.validate_license(lic.key)

    async def test_validate_expired_license(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS, valid_days=0)
        # Force expiry in the past
        lic.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        await db_session.commit()

        with pytest.raises(LicenseError, match="verlopen"):
            await lm.validate_license(lic.key)

    async def test_validate_quota_exceeded(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        # Exhaust quota
        lic.queries_used = TIER_LIMITS[LicenseTier.BASIS]["queries_per_month"]
        await db_session.commit()

        with pytest.raises(LicenseError, match="querylimiet"):
            await lm.validate_license(lic.key)


@pytest.mark.asyncio
class TestQueryRecording:
    async def test_record_query_increments(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        assert lic.queries_used == 0

        await lm.record_query(lic.key)
        await db_session.refresh(lic)
        assert lic.queries_used == 1

        await lm.record_query(lic.key)
        await db_session.refresh(lic)
        assert lic.queries_used == 2

    async def test_record_query_invalid_key_ignored(self, db_session):
        lm = LicenseManager(db_session)
        # Should not raise
        await lm.record_query("NONEXISTENT-KEY")


@pytest.mark.asyncio
class TestLicenseInfo:
    async def test_get_license_info(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Test Org", LicenseTier.PROFESSIONAL)
        info = await lm.get_license_info(lic.key)
        assert info["organization"] == "Test Org"
        assert info["tier"] == "professional"
        assert info["queries_limit"] == 1000
        assert info["users_limit"] == 15
        assert info["queries_used"] == 0


@pytest.mark.asyncio
class TestUserCount:
    async def test_check_user_count_within_limit(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)
        assert await lm.check_user_count(lic.key) is True

    async def test_check_user_count_at_limit(self, db_session):
        lm = LicenseManager(db_session)
        lic = await lm.create_license("Org", LicenseTier.BASIS)  # max 3 users

        from app.core.auth import hash_password

        for i in range(3):
            user = User(
                email=f"user{i}@test.com",
                hashed_password=hash_password("pass"),
                full_name=f"User {i}",
                organization="Org",
                license_key=lic.key,
            )
            db_session.add(user)
        await db_session.commit()

        assert await lm.check_user_count(lic.key) is False
