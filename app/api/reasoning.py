"""Reasoning API — LLM-powered causal reasoning using the DAG."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
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
    query: str = Field(..., min_length=1, max_length=5000)
    provider: str = Field("openai", pattern=r"^(openai|anthropic)$")
    api_key: str = Field(..., min_length=10, max_length=256)
    model: str | None = Field(None, max_length=100)
    factor_ids: list[str] | None = None


class InterventionReasoningRequest(BaseModel):
    factor_id: str = Field(..., min_length=1, max_length=200)
    change: float
    description: str = Field("", max_length=2000)
    provider: str = Field("openai", pattern=r"^(openai|anthropic)$")
    api_key: str = Field(..., min_length=10, max_length=256)
    model: str | None = Field(None, max_length=100)


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
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e)))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        )

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
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e)))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        )

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


@router.post("/query/validated")
async def reason_query_validated(
    request: ReasoningRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Ask a reasoning question with automatic factor selection and response validation.

    1. Auto-selects relevant factors from the query if none provided
    2. Generates LLM response
    3. Validates the response against the model
    """
    await _check_license(user, db)

    # Auto-select factors if not provided
    factor_ids = request.factor_ids
    auto_selected = False
    if not factor_ids:
        relevant = dag.find_relevant_factors(request.query, max_results=8)
        if relevant:
            factor_ids = [f["id"] for f in relevant]
            auto_selected = True

    builder = PromptBuilder(dag)
    messages = builder.build_full_prompt(request.query, factor_ids)

    connector = LLMConnector(request.provider, request.api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e)))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        )

    # Validate response
    validation = dag.validate_response_factors(response)

    # Record usage
    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    return {
        "query": request.query,
        "response": response,
        "model_version": dag.version,
        "factors_used": factor_ids,
        "auto_selected": auto_selected,
        "validation": validation,
    }


def _format_llm_error(error_msg: str) -> str:
    """Translate LLM provider errors to user-friendly Dutch messages."""
    msg = error_msg.lower()
    if "401" in msg or "invalid" in msg or "unauthorized" in msg:
        return "Je API key is ongeldig. Controleer de key in je LLM configuratie."
    if "429" in msg or "rate" in msg:
        return "De AI-service heeft een rate limit bereikt. Wacht enkele minuten en probeer het opnieuw."
    if "timeout" in msg:
        return "Het antwoord duurde te lang. Probeer het later opnieuw."
    if "500" in msg or "internal" in msg:
        return "De AI-service heeft een interne fout. Probeer het later opnieuw."
    return "De AI-service kon het verzoek niet verwerken. Probeer het later opnieuw."


async def _check_license(user: User, db: AsyncSession) -> None:
    if not user.license_key:
        raise HTTPException(status_code=403, detail="Geen licentie gekoppeld")
    lm = LicenseManager(db)
    try:
        await lm.validate_license(user.license_key)
    except Exception:
        raise HTTPException(status_code=403, detail="Licentie is ongeldig of verlopen")
