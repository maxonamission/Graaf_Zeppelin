"""Models API — List and switch between causal graph models (S10-05)."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.core.audit import audit_log
from app.core.dag_engine import CausalDAG
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/models", tags=["models"])


class SwitchModelRequest(BaseModel):
    model_id: str  # filename without .json


@router.get("")
async def list_models(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all available causal graph models in data/models/.

    Returns model metadata (name, version, factor/relation counts)
    without fully loading each model.
    """
    models_dir = Path(settings.dag_models_path)
    if not models_dir.exists():
        return {"models": [], "count": 0}

    models = []
    for path in sorted(models_dir.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)

            # Extract basic metadata without full load
            meta = data.get("metadata", {})
            is_v2 = "nodes" in data

            if is_v2:
                summary = meta.get("summary", {})
                models.append({
                    "id": path.stem,
                    "filename": path.name,
                    "name": meta.get("project", path.stem),
                    "version": meta.get("version", "?"),
                    "description": summary.get("description", ""),
                    "num_factors": len(data.get("nodes", [])),
                    "num_relations": len(data.get("edges", [])),
                    "num_sliders": len(data.get("sliders", [])),
                    "schema": "v2",
                })
            else:
                models.append({
                    "id": path.stem,
                    "filename": path.name,
                    "name": data.get("name", path.stem),
                    "version": data.get("version", "?"),
                    "description": data.get("description", ""),
                    "num_factors": len(data.get("factors", [])),
                    "num_relations": len(data.get("relations", [])),
                    "num_sliders": 0,
                    "schema": "v1",
                })
        except (json.JSONDecodeError, KeyError):
            continue

    return {"models": models, "count": len(models)}


@router.get("/current")
async def current_model(
    user: User = Depends(get_current_user),
):
    """Get the currently active model ID and summary."""
    from fastapi import Request

    # Get the DAG from app state
    from app.main import app
    dag: CausalDAG = getattr(app.state, "dag", None)
    if not dag:
        raise HTTPException(status_code=503, detail="Model niet geladen")

    current_path = Path(settings.graph_model_path)
    return {
        "model_id": current_path.stem,
        "name": dag.name,
        "version": dag.version,
        "num_factors": dag.graph.number_of_nodes(),
        "num_relations": dag.graph.number_of_edges(),
    }


@router.post("/switch")
async def switch_model(
    request: SwitchModelRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Switch to a different causal graph model.

    Restricted to admin users to prevent a single user from affecting
    all other users (the DAG is shared app state).
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Alleen beheerders kunnen het actieve model wisselen",
        )

    models_dir = Path(settings.dag_models_path)
    model_path = models_dir / f"{request.model_id}.json"

    if not model_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Model niet gevonden",
        )

    try:
        new_dag = CausalDAG.load(str(model_path))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Kon model niet laden",
        )

    # Update app state
    from app.main import app
    app.state.dag = new_dag

    # Update config to reflect new active model
    settings.graph_model_path = str(model_path)
    audit_log("model_switched", user_id=user.id, model_id=request.model_id)

    return {
        "switched": True,
        "model_id": request.model_id,
        "name": new_dag.name,
        "version": new_dag.version,
        "num_factors": new_dag.graph.number_of_nodes(),
        "num_relations": new_dag.graph.number_of_edges(),
    }
