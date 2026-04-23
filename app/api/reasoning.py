"""Reasoning API — LLM-powered causal reasoning using the DAG."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_dag
from app.core.audit import audit_log
from app.core.dag_engine import CausalDAG
from app.core.key_vault import KeyVault
from app.core.license_manager import LicenseManager
from app.core.llm_connector import LLMConnector, LLMProviderError
from app.core.llm_guard import (
    check_prompt_injection,
    check_prompt_leakage_attempt,
    sanitize_llm_output,
)
from app.core.prompt_builder import PromptBuilder
from app.db import get_db
from app.models.user import User
from app.models.user_api_key import UserApiKey

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])


class ReasoningRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    provider: str = Field("openai", pattern=r"^(openai|anthropic)$")
    stored_key_id: int = Field(..., description="ID van opgeslagen API key")
    model: str | None = Field(None, max_length=100)
    factor_ids: list[str] | None = None


class InterventionReasoningRequest(BaseModel):
    factor_id: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    change: float
    description: str = Field("", max_length=2000)
    provider: str = Field("openai", pattern=r"^(openai|anthropic)$")
    stored_key_id: int = Field(..., description="ID van opgeslagen API key")
    model: str | None = Field(None, max_length=100)


@router.post("/query")
async def reason_query(
    request: ReasoningRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Ask a causal reasoning question. Uses the DAG to constrain LLM reasoning."""
    await _check_license_and_quota(user, db)

    # LLM01/LLM07: Guard against prompt injection and system prompt extraction
    _guard_user_input(request.query, user.id)

    # S07-04: Resolve stored key if sentinel
    api_key = await _resolve_api_key(request.stored_key_id, request.provider, user.id, db)

    builder = PromptBuilder(dag)
    messages = builder.build_full_prompt(request.query, request.factor_ids)

    connector = LLMConnector(request.provider, api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        logger.warning("LLM provider error (query, user=%s): %s", user.id, e)
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e))) from e
    except Exception as e:
        logger.exception("Unexpected LLM error (query, user=%s)", user.id)
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        ) from e

    # LLM05: Sanitize LLM output before returning to client
    response = sanitize_llm_output(response)

    # Record usage
    await _record_usage(user, db)

    audit_log("reasoning_query", user_id=user.id, provider=request.provider)

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
    await _check_license_and_quota(user, db)

    # LLM01/LLM07: Guard against prompt injection
    if request.description:
        _guard_user_input(request.description, user.id)

    # S07-04: Resolve stored key if sentinel
    api_key = await _resolve_api_key(request.stored_key_id, request.provider, user.id, db)

    builder = PromptBuilder(dag)

    system_prompt = builder.build_system_prompt()
    intervention_prompt = builder.build_intervention_prompt(
        request.factor_id, request.change, request.description
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": intervention_prompt},
    ]

    connector = LLMConnector(request.provider, api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        logger.warning("LLM provider error (intervene, user=%s): %s", user.id, e)
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e))) from e
    except Exception as e:
        logger.exception("Unexpected LLM error (intervene, user=%s)", user.id)
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        ) from e

    # LLM05: Sanitize LLM output
    response = sanitize_llm_output(response)

    # Also include raw simulation data
    effects = dag.simulate_intervention(request.factor_id, request.change)

    await _record_usage(user, db)

    audit_log(
        "reasoning_intervention",
        user_id=user.id,
        provider=request.provider,
        factor_id=request.factor_id,
    )

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
    await _check_license_and_quota(user, db)

    # LLM01/LLM07: Guard against prompt injection
    _guard_user_input(request.query, user.id)

    # S07-04: Resolve stored key if sentinel
    api_key = await _resolve_api_key(request.stored_key_id, request.provider, user.id, db)

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

    connector = LLMConnector(request.provider, api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError as e:
        logger.warning("LLM provider error (validated, user=%s): %s", user.id, e)
        raise HTTPException(status_code=502, detail=_format_llm_error(str(e))) from e
    except Exception as e:
        logger.exception("Unexpected LLM error (validated, user=%s)", user.id)
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar. Probeer het later opnieuw.",
        ) from e

    # LLM05: Sanitize LLM output
    response = sanitize_llm_output(response)

    # Validate response
    validation = dag.validate_response_factors(response)

    # Record usage
    await _record_usage(user, db)

    audit_log("reasoning_query_validated", user_id=user.id, provider=request.provider)

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


async def _check_license_and_quota(user: User, db: AsyncSession) -> None:
    """Check license validity and free-tier daily quota (S07-01)."""
    lm = LicenseManager(db)

    if not user.license_key:
        # No license → check free tier quota
        usage = await lm.get_daily_usage(user.id)
        if usage["remaining"] <= 0:
            raise HTTPException(
                status_code=403,
                detail="Je dagelijkse gratis vragen zijn op. Upgrade naar een betaald account voor meer vragen.",
            )
        return

    # Has license → check license validity
    try:
        license_obj = await lm.validate_license(user.license_key)
        # Free tier with license also has daily limits
        if license_obj.tier == "free":
            usage = await lm.get_daily_usage(user.id)
            if usage["remaining"] <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="Je dagelijkse gratis vragen zijn op. Upgrade naar een betaald account voor meer vragen.",
                )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=403, detail="Licentie is ongeldig of verlopen") from exc


async def _record_usage(user: User, db: AsyncSession) -> None:
    """Record query usage for both licensed and free-tier users."""
    lm = LicenseManager(db)
    if user.license_key:
        await lm.record_query(user.license_key)
        # Also record free tier usage if on free tier
        try:
            license_obj = await lm.validate_license(user.license_key)
            if license_obj.tier == "free":
                await lm.record_free_query(user.id)
        except Exception:
            pass
    else:
        await lm.record_free_query(user.id)


def _guard_user_input(user_input: str, user_id: int) -> None:
    """Check user input for prompt injection and leakage attempts (LLM01/LLM07)."""
    injection = check_prompt_injection(user_input)
    if injection:
        audit_log("prompt_injection_blocked", user_id=user_id, matched=injection)
        raise HTTPException(
            status_code=400,
            detail="Je vraag bevat patronen die niet zijn toegestaan. Herformuleer je vraag.",
        )
    leakage = check_prompt_leakage_attempt(user_input)
    if leakage:
        audit_log("prompt_leakage_blocked", user_id=user_id, matched=leakage)
        raise HTTPException(
            status_code=400,
            detail="Je vraag bevat patronen die niet zijn toegestaan. Herformuleer je vraag.",
        )


async def _resolve_api_key(
    stored_key_id: int, provider: str, user_id: int, db: AsyncSession
) -> str:
    """Resolve a stored API key by ID (S11-02: no raw keys in requests)."""
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.id == stored_key_id,
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider,
            UserApiKey.is_active == True,  # noqa: E712
        )
    )
    key_obj = result.scalar_one_or_none()
    if not key_obj:
        raise HTTPException(
            status_code=422,
            detail="Geen opgeslagen API key gevonden. Sla eerst een key op via de LLM-configuratie.",
        )
    vault = KeyVault()
    return vault.decrypt(key_obj.encrypted_key)
