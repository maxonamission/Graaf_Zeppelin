"""Graph API — DAG queries, factor info, and interventions."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.dag_engine import CausalDAG
from app.core.license_manager import LicenseManager
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/graph", tags=["graph"])


def _load_dag() -> CausalDAG:
    """Load the current DAG model."""
    return CausalDAG.load("data/models/sportdeelname_v1.json")


class InterventionRequest(BaseModel):
    factor_id: str
    change: float  # -1.0 to 1.0


@router.get("/summary")
async def graph_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get model summary — factor count, relations, metadata."""
    await _check_license(user, db)
    dag = _load_dag()
    return dag.get_graph_summary()


@router.get("/factors")
async def list_factors(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all factors in the model."""
    await _check_license(user, db)
    dag = _load_dag()
    return {"factors": dag.get_all_factors()}


@router.get("/factors/{factor_id}")
async def get_factor(
    factor_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed info about a specific factor."""
    await _check_license(user, db)
    dag = _load_dag()
    info = dag.get_factor_info(factor_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Factor '{factor_id}' niet gevonden")
    return info


@router.get("/relations")
async def list_relations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all causal relations."""
    await _check_license(user, db)
    dag = _load_dag()
    return {"relations": dag.get_all_relations()}


@router.get("/paths/{source}/{target}")
async def causal_paths(
    source: str,
    target: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Find all causal paths between two factors."""
    await _check_license(user, db)
    dag = _load_dag()
    paths = dag.get_causal_paths(source, target)
    return {"source": source, "target": target, "paths": paths}


@router.post("/intervene")
async def simulate_intervention(
    request: InterventionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Simulate a causal intervention and see propagated effects."""
    await _check_license(user, db)
    dag = _load_dag()

    info = dag.get_factor_info(request.factor_id)
    if not info:
        raise HTTPException(
            status_code=404, detail=f"Factor '{request.factor_id}' niet gevonden"
        )

    effects = dag.simulate_intervention(request.factor_id, request.change)

    # Record query usage
    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    return {
        "factor": request.factor_id,
        "change": request.change,
        "effects": effects,
    }


async def _check_license(user: User, db: AsyncSession) -> None:
    """Verify the user's license is still valid."""
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")
    lm = LicenseManager(db)
    try:
        await lm.validate_license(user.license_key)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
