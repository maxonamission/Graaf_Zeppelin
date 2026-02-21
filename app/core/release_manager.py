"""
Release Manager — Handles versioning, release notes, and migration.

Prevents trend breaks by treating major releases differently:
- Parallel run period (old + new model)
- Migration guides
- Comparison reports
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.release import Release


class ReleaseManager:
    """Manages releases, versioning, and migration."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_release(
        self,
        version: str,
        title: str,
        description: str,
        is_major: bool = False,
        migration_guide: str | None = None,
    ) -> Release:
        """Create a new release with release notes."""
        if not self._validate_version(version):
            raise ValueError(
                f"Invalid version format '{version}'. Use semantic versioning (e.g. 1.2.3)"
            )

        if is_major and not migration_guide:
            raise ValueError("Major releases require a migration guide")

        release = Release(
            version=version,
            title=title,
            description=description,
            is_major=is_major,
            migration_guide=migration_guide,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(release)
        await self.db.commit()
        await self.db.refresh(release)
        return release

    async def get_releases(self, limit: int = 20) -> list[Release]:
        """Get recent releases, newest first."""
        result = await self.db.execute(
            select(Release).order_by(Release.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())

    async def get_release(self, version: str) -> Release | None:
        """Get a specific release by version."""
        result = await self.db.execute(
            select(Release).where(Release.version == version)
        )
        return result.scalar_one_or_none()

    async def get_latest_version(self) -> str | None:
        """Get the most recent version string."""
        result = await self.db.execute(
            select(Release).order_by(Release.created_at.desc()).limit(1)
        )
        release = result.scalar_one_or_none()
        return release.version if release else None

    @staticmethod
    def _validate_version(version: str) -> bool:
        """Validate semantic version format."""
        return bool(re.match(r"^\d+\.\d+\.\d+$", version))
