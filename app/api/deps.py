"""Shared API dependencies — current user, license validation, graph access."""

from __future__ import annotations

from fastapi import Cookie, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import decode_access_token
from app.core.dag_engine import CausalDAG
from app.db import get_db
from app.models.user import User, UserRole


def require_role(*roles: UserRole):
    """Dependency factory: restrict endpoint to users with one of the given roles (S11-03)."""

    async def _check(user: User = Depends(get_current_user)) -> User:
        if user.role not in {r.value for r in roles}:
            raise HTTPException(
                status_code=403,
                detail="Onvoldoende rechten voor deze actie",
            )
        return user

    return _check


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


def get_dag(request: Request) -> CausalDAG:
    """Get the cached CausalDAG from application state."""
    dag = getattr(request.app.state, "dag", None)
    if dag is None:
        raise HTTPException(status_code=503, detail="Graph model niet geladen")
    return dag


async def get_user_dag(
    request: Request,
    user: User = Depends(get_current_user),
) -> CausalDAG:
    """Get the DAG respecting the user's preferred model (S11-03).

    Falls back to the global default if no preference is set or the
    preferred model cannot be loaded.
    """
    default_dag = getattr(request.app.state, "dag", None)
    if default_dag is None:
        raise HTTPException(status_code=503, detail="Graph model niet geladen")

    if not user.preferred_model:
        return default_dag

    from pathlib import Path

    from app.config import settings

    model_path = Path(settings.dag_models_path) / f"{user.preferred_model}.json"
    if not model_path.exists():
        return default_dag

    # Cache per-user models on app state to avoid reloading every request
    cache = getattr(request.app.state, "_model_cache", None)
    if cache is None:
        cache = {}
        request.app.state._model_cache = cache

    if user.preferred_model not in cache:
        cache[user.preferred_model] = CausalDAG.load(str(model_path))

    return cache[user.preferred_model]
