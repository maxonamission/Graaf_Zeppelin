"""Explorations API — Save and load policy exploration sessions (S05-01)."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db import get_db
from app.models.exploration import Exploration
from app.models.user import User

router = APIRouter(prefix="/api/explorations", tags=["explorations"])


class SaveExplorationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    question: str = Field(..., min_length=1, max_length=5000)
    slider_values: dict[str, float] = Field(default_factory=dict)
    effects: list[dict] = Field(default_factory=list)
    advice: str | None = None
    model_version: str | None = None


@router.post("")
async def save_exploration(
    request: SaveExplorationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a policy exploration for later retrieval."""
    exploration = Exploration(
        user_id=user.id,
        title=request.title,
        question=request.question,
        slider_values_json=json.dumps(request.slider_values),
        effects_json=json.dumps(request.effects),
        advice=request.advice,
        model_version=request.model_version,
    )
    db.add(exploration)
    await db.commit()
    await db.refresh(exploration)

    return {
        "id": exploration.id,
        "title": exploration.title,
        "created_at": exploration.created_at.isoformat(),
    }


@router.get("")
async def list_explorations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List saved explorations for the current user, most recent first."""
    result = await db.execute(
        select(Exploration)
        .where(Exploration.user_id == user.id)
        .order_by(Exploration.updated_at.desc())
        .limit(50)
    )
    explorations = result.scalars().all()

    return {
        "explorations": [
            {
                "id": e.id,
                "title": e.title,
                "question": e.question,
                "created_at": e.created_at.isoformat(),
                "has_advice": e.advice is not None,
            }
            for e in explorations
        ]
    }


@router.get("/{exploration_id}")
async def get_exploration(
    exploration_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Load a saved exploration with full details."""
    result = await db.execute(
        select(Exploration).where(
            Exploration.id == exploration_id,
            Exploration.user_id == user.id,
        )
    )
    exploration = result.scalar_one_or_none()
    if not exploration:
        raise HTTPException(status_code=404, detail="Verkenning niet gevonden")

    return {
        "id": exploration.id,
        "title": exploration.title,
        "question": exploration.question,
        "slider_values": json.loads(exploration.slider_values_json),
        "effects": json.loads(exploration.effects_json),
        "advice": exploration.advice,
        "model_version": exploration.model_version,
        "created_at": exploration.created_at.isoformat(),
    }


@router.delete("/{exploration_id}")
async def delete_exploration(
    exploration_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a saved exploration."""
    result = await db.execute(
        select(Exploration).where(
            Exploration.id == exploration_id,
            Exploration.user_id == user.id,
        )
    )
    exploration = result.scalar_one_or_none()
    if not exploration:
        raise HTTPException(status_code=404, detail="Verkenning niet gevonden")

    await db.delete(exploration)
    await db.commit()
    return {"deleted": True}
