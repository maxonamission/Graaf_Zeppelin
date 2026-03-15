"""Tests for the ReleaseManager — versioning, release creation, and validation."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.release_manager import ReleaseManager
from app.models.base import Base


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


class TestVersionValidation:
    def test_valid_versions(self):
        assert ReleaseManager._validate_version("1.0.0")
        assert ReleaseManager._validate_version("0.1.0")
        assert ReleaseManager._validate_version("10.20.30")

    def test_invalid_versions(self):
        assert not ReleaseManager._validate_version("1.0")
        assert not ReleaseManager._validate_version("v1.0.0")
        assert not ReleaseManager._validate_version("1.0.0-beta")
        assert not ReleaseManager._validate_version("abc")
        assert not ReleaseManager._validate_version("")


@pytest.mark.asyncio
class TestReleaseCreation:
    async def test_create_minor_release(self, db_session):
        rm = ReleaseManager(db_session)
        release = await rm.create_release(
            version="1.0.0",
            title="Initial release",
            description="First version",
        )
        assert release.version == "1.0.0"
        assert release.title == "Initial release"
        assert release.is_major is False
        assert release.migration_guide is None

    async def test_create_major_release(self, db_session):
        rm = ReleaseManager(db_session)
        release = await rm.create_release(
            version="2.0.0",
            title="Major update",
            description="Breaking changes",
            is_major=True,
            migration_guide="Step 1: update config...",
        )
        assert release.is_major is True
        assert release.migration_guide == "Step 1: update config..."

    async def test_major_release_requires_migration_guide(self, db_session):
        rm = ReleaseManager(db_session)
        with pytest.raises(ValueError, match="migration guide"):
            await rm.create_release(
                version="2.0.0",
                title="Major",
                description="Breaking",
                is_major=True,
            )

    async def test_invalid_version_format(self, db_session):
        rm = ReleaseManager(db_session)
        with pytest.raises(ValueError, match="Invalid version format"):
            await rm.create_release(
                version="bad",
                title="Test",
                description="Test",
            )


@pytest.mark.asyncio
class TestReleaseQueries:
    async def test_get_releases(self, db_session):
        rm = ReleaseManager(db_session)
        await rm.create_release("1.0.0", "First", "Initial")
        await rm.create_release("1.1.0", "Second", "Update")

        releases = await rm.get_releases()
        assert len(releases) == 2

    async def test_get_release_by_version(self, db_session):
        rm = ReleaseManager(db_session)
        await rm.create_release("1.0.0", "First", "Initial")
        await rm.create_release("1.1.0", "Second", "Update")

        release = await rm.get_release("1.0.0")
        assert release is not None
        assert release.title == "First"

    async def test_get_nonexistent_release(self, db_session):
        rm = ReleaseManager(db_session)
        release = await rm.get_release("99.99.99")
        assert release is None

    async def test_get_latest_version(self, db_session):
        rm = ReleaseManager(db_session)
        assert await rm.get_latest_version() is None

        await rm.create_release("1.0.0", "First", "Initial")
        await rm.create_release("1.1.0", "Second", "Update")

        latest = await rm.get_latest_version()
        assert latest == "1.1.0"

    async def test_releases_ordered_newest_first(self, db_session):
        rm = ReleaseManager(db_session)
        await rm.create_release("1.0.0", "First", "A")
        await rm.create_release("1.1.0", "Second", "B")
        await rm.create_release("1.2.0", "Third", "C")

        releases = await rm.get_releases()
        versions = [r.version for r in releases]
        assert versions == ["1.2.0", "1.1.0", "1.0.0"]

    async def test_get_releases_with_limit(self, db_session):
        rm = ReleaseManager(db_session)
        for i in range(5):
            await rm.create_release(f"1.{i}.0", f"Release {i}", f"Desc {i}")

        releases = await rm.get_releases(limit=3)
        assert len(releases) == 3
