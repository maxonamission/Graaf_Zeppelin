"""Reasoning API — LLM-powered causal reasoning using the DAG."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_dag
from app.core.dag_engine import CausalDAG
from app.core.license_manager import LicenseManager
from app.core.llm_connector import LLMConnector, LLMProviderError
from app.core.prompt_builder import PromptBuilder
from app.db import get_db
from app.models.user import User

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])


class ReasoningRequest(BaseModel):
    query: str
    provider: str = "openai"
    api_key: str
    model: str | None = None
    factor_ids: list[str] | None = None


class InterventionReasoningRequest(BaseModel):
    factor_id: str
    change: float
    description: str = ""
    provider: str = "openai"
    api_key: str
    model: str | None = None


@router.post("/query")
async def reason_query(
    request: ReasoningRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Ask a causal reasoning question. Uses the DAG to constrain LLM reasoning."""
    await _check_license(user, db)

    builder = PromptBuilder(dag)
    messages = builder.build_full_prompt(request.query, request.factor_ids)

    connector = LLMConnector(request.provider, request.api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        raise HTTPException(status_code=502, detail=f"LLM fout: {e}")

    # Record usage
    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    return {
        "query": request.query,
        "response": response,
        "model_version": dag.version,
        "factors_used": request.factor_ids,
    }


@router.post("/intervene")
async def reason_intervention(
    request: InterventionReasoningRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Analyse an intervention using DAG + LLM reasoning."""
    await _check_license(user, db)

    builder = PromptBuilder(dag)

    system_prompt = builder.build_system_prompt()
    intervention_prompt = builder.build_intervention_prompt(
        request.factor_id, request.change, request.description
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": intervention_prompt},
    ]

    connector = LLMConnector(request.provider, request.api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        raise HTTPException(status_code=502, detail=f"LLM fout: {e}")

    # Also include raw simulation data
    effects = dag.simulate_intervention(request.factor_id, request.change)

    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    return {
        "factor": request.factor_id,
        "change": request.change,
        "analysis": response,
        "simulation": effects,
        "model_version": dag.version,
    }


async def _check_license(user: User, db: AsyncSession) -> None:
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")
    lm = LicenseManager(db)
    try:
        await lm.validate_license(user.license_key)
    except Exception as e:
        raise HTTPException(status_code=403, detail=str(e))
