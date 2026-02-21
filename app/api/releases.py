"""Releases API — release notes and version management."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.release_manager import ReleaseManager
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/releases", tags=["releases"])


@router.get("/")
async def list_releases(
    limit: int = 20,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get recent release notes."""
    rm = ReleaseManager(db)
    releases = await rm.get_releases(limit=limit)
    return {
        "releases": [
            {
                "version": r.version,
                "title": r.title,
                "description": r.description,
                "is_major": r.is_major,
                "migration_guide": r.migration_guide,
                "created_at": r.created_at.isoformat(),
            }
            for r in releases
        ]
    }


@router.get("/latest")
async def latest_release(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the latest version info."""
    rm = ReleaseManager(db)
    version = await rm.get_latest_version()
    return {"latest_version": version}
