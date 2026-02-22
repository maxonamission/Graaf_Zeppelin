"""Graph API — DAG queries, factor info, domains, sliders, and simulations."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_dag
from app.core.dag_engine import CausalDAG
from app.core.license_manager import LicenseManager
from app.core.slider_engine import apply_slider, simulate_sliders
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/graph", tags=["graph"])


class InterventionRequest(BaseModel):
    factor_id: str
    change: float  # -1.0 to 1.0


class SliderInput(BaseModel):
    id: str
    value: float  # 0.0 to 1.0


class SimulateRequest(BaseModel):
    sliders: list[SliderInput]


class QualifierAnswer(BaseModel):
    slider_id: str
    answers: list[float]  # one value per qualifier question


class QualifyRequest(BaseModel):
    responses: list[QualifierAnswer]


# ── Summary & metadata ──────────────────────────────────────────────────


@router.get("/summary")
async def graph_summary(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get model summary — factor count, relations, domains, sliders, metrics."""
    await _check_license(user, db)
    return dag.get_graph_summary()


# ── Domains ──────────────────────────────────────────────────────────────


@router.get("/domains")
async def list_domains(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get all domains with node counts."""
    await _check_license(user, db)
    return {"domains": dag.get_domains()}


# ── Factors (nodes) ─────────────────────────────────────────────────────


@router.get("/factors")
async def list_factors(
    domain: str | None = Query(None, description="Filter by domain"),
    cluster: str | None = Query(None, description="Filter by cluster"),
    status: str | None = Query(None, description="Filter by status (A, B, -)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """List all factors, optionally filtered by domain, cluster, or status."""
    await _check_license(user, db)
    factors = dag.get_all_factors(domain=domain, cluster=cluster, status=status)
    return {"factors": factors, "count": len(factors)}


@router.get("/factors/{factor_id}")
async def get_factor(
    factor_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get detailed info about a specific factor with causes, effects, and moderators."""
    await _check_license(user, db)
    info = dag.get_factor_info(factor_id)
    if not info:
        raise HTTPException(status_code=404, detail=f"Factor '{factor_id}' niet gevonden")
    return info


# ── Relations (edges) ───────────────────────────────────────────────────


@router.get("/relations")
async def list_relations(
    cluster: str | None = Query(None, description="Filter by cluster"),
    polarity: str | None = Query(None, description="Filter by polarity (positive, negative)"),
    edge_type: str | None = Query(None, description="Filter by edge type"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """List all causal relations, optionally filtered."""
    await _check_license(user, db)
    relations = dag.get_all_relations(
        cluster=cluster, polarity=polarity, edge_type=edge_type
    )
    return {"relations": relations, "count": len(relations)}


# ── Paths ────────────────────────────────────────────────────────────────


@router.get("/paths/{source}/{target}")
async def causal_paths(
    source: str,
    target: str,
    max_length: int = Query(5, ge=1, le=10, description="Max path length"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Find all causal paths between two factors."""
    await _check_license(user, db)
    paths = dag.get_causal_paths(source, target, max_length=max_length)
    return {"source": source, "target": target, "paths": paths, "count": len(paths)}


# ── Intervention ─────────────────────────────────────────────────────────


@router.post("/intervene")
async def simulate_intervention(
    request: InterventionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Simulate a causal intervention and see propagated effects."""
    await _check_license(user, db)

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


# ── Sliders ──────────────────────────────────────────────────────────────


@router.get("/sliders")
async def list_sliders(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get all policy sliders with their definitions and curves."""
    await _check_license(user, db)
    return {"sliders": dag.get_sliders(), "count": len(dag.sliders)}


# ── Slider qualification ─────────────────────────────────────────────────
# NOTE: These routes MUST be registered before /sliders/{slider_id}
# to prevent FastAPI from matching "qualify" as a slider_id.


@router.get("/sliders/qualify/relevant")
async def get_relevant_qualifiers(
    factor_ids: str = Query(
        ..., description="Comma-separated factor IDs to find relevant sliders for"
    ),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get qualifying questions only for sliders relevant to the given factors.

    This prevents the agent from asking all 8x2 questions every time.
    Only sliders whose related_nodes or primary_clusters overlap with
    the queried factors are returned.
    """
    await _check_license(user, db)
    ids = [fid.strip() for fid in factor_ids.split(",") if fid.strip()]
    relevant = dag.get_relevant_sliders(ids)
    result = []
    for slider in relevant:
        qualifiers = slider.get("qualifiers", [])
        if qualifiers:
            result.append({
                "slider_id": slider["id"],
                "slider_label": slider.get("label", ""),
                "qualifiers": qualifiers,
            })
    return {
        "factor_ids": ids,
        "sliders": result,
        "count": len(result),
    }


@router.get("/sliders/{slider_id}")
async def get_slider(
    slider_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get a single slider by ID."""
    await _check_license(user, db)
    slider = dag.get_slider(slider_id)
    if not slider:
        raise HTTPException(status_code=404, detail=f"Slider '{slider_id}' niet gevonden")
    return slider


@router.get("/sliders/{slider_id}/qualify")
async def get_slider_qualifiers(
    slider_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Get qualifying questions for a specific slider."""
    await _check_license(user, db)
    qualifiers = dag.get_slider_qualifiers(slider_id)
    if qualifiers is None:
        raise HTTPException(status_code=404, detail=f"Slider '{slider_id}' niet gevonden")
    slider = dag.get_slider(slider_id)
    return {
        "slider_id": slider_id,
        "slider_label": slider.get("label", ""),
        "qualifiers": qualifiers,
        "count": len(qualifiers),
    }


@router.post("/sliders/qualify")
async def resolve_qualifiers(
    request: QualifyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Convert qualifier answers into slider values.

    Takes the user's answers to qualifying questions and computes the
    average value per slider, ready for use in /simulate.
    """
    await _check_license(user, db)
    slider_values = {}
    for response in request.responses:
        slider = dag.get_slider(response.slider_id)
        if not slider:
            raise HTTPException(
                status_code=404,
                detail=f"Slider '{response.slider_id}' niet gevonden",
            )
        qualifiers = slider.get("qualifiers", [])
        if not qualifiers:
            raise HTTPException(
                status_code=422,
                detail=f"Slider '{response.slider_id}' heeft geen kwalificerende vragen",
            )
        if len(response.answers) != len(qualifiers):
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Slider '{response.slider_id}' verwacht {len(qualifiers)} "
                    f"antwoorden, maar kreeg er {len(response.answers)}"
                ),
            )
        for val in response.answers:
            if not 0.0 <= val <= 1.0:
                raise HTTPException(
                    status_code=422,
                    detail="Antwoordwaarden moeten tussen 0 en 1 liggen",
                )
        slider_values[response.slider_id] = round(
            sum(response.answers) / len(response.answers), 4
        )

    return {
        "slider_values": slider_values,
        "count": len(slider_values),
    }


# ── Slider simulation ───────────────────────────────────────────────────


@router.post("/simulate")
async def simulate_slider_changes(
    request: SimulateRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Simulate the effect of changing one or more policy sliders.

    Adjusts edge weights based on slider curves and sensitivity ratings.
    """
    await _check_license(user, db)

    # Validate sliders exist
    slider_values = {}
    for s in request.sliders:
        slider_def = dag.get_slider(s.id)
        if not slider_def:
            raise HTTPException(
                status_code=404, detail=f"Slider '{s.id}' niet gevonden"
            )
        if not 0.0 <= s.value <= 1.0:
            raise HTTPException(
                status_code=422, detail=f"Slider value must be between 0 and 1"
            )
        slider_values[s.id] = s.value

    # Get all edges as dicts for the slider engine
    edges = dag.get_all_relations()

    effects = simulate_sliders(dag.sliders, slider_values, edges)

    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    return {
        "slider_values": slider_values,
        "affected_edges": effects,
        "count": len(effects),
    }


# ── Helpers ──────────────────────────────────────────────────────────────


async def _check_license(user: User, db: AsyncSession) -> None:
    """Verify the user's license is still valid."""
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")
    lm = LicenseManager(db)
    try:
        await lm.validate_license(user.license_key)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
