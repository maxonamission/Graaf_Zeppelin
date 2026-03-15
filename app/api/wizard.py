"""Wizard API — Guided policy exploration flow.

Implements the step-by-step wizard:
1. User enters a policy question
2. App suggests relevant sliders (AI can propose, user validates)
3. User answers qualification questions per slider
4. Simulation runs with qualified values
5. Results presented as recommendations in plain language (B2)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.api.deps import get_current_user, get_dag
from app.core.dag_engine import CausalDAG
from app.core.key_vault import KeyVault
from app.core.license_manager import LicenseManager
from app.core.llm_connector import LLMConnector, LLMProviderError
from app.core.slider_engine import simulate_sliders
from app.db import get_db
from app.models.user import User
from app.models.user_api_key import UserApiKey

router = APIRouter(prefix="/api/wizard", tags=["wizard"])


# ── Request / Response models ──────────────────────────────────────────


class PolicyQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)


class QualificationAnswer(BaseModel):
    slider_id: str
    answers: list[float]  # one value per qualifier question (0–1)


class SimulateQualifiedRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    slider_values: dict[str, float]  # already resolved slider values


class GenerateAdviceRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=5000)
    slider_values: dict[str, float]
    effects: list[dict] | None = None
    provider: str = Field("openai", pattern=r"^(openai|anthropic)$")
    api_key: str = Field(..., min_length=1, max_length=256)
    model: str | None = Field(None, max_length=100)


# ── Step 1: Analyse question → suggest sliders ────────────────────────


@router.post("/analyse")
async def analyse_question(
    request: PolicyQuestionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Analyse a policy question and suggest relevant sliders with qualifiers.

    Returns relevant sliders and their qualification questions so the user
    can answer them in step 2.
    """
    await _check_license(user, db)

    # Find relevant factors from the question
    relevant_factors = dag.find_relevant_factors(request.question, max_results=12)
    factor_ids = [f["id"] for f in relevant_factors]

    # Find sliders relevant to those factors
    relevant_sliders = dag.get_relevant_sliders(factor_ids) if factor_ids else dag.get_sliders()

    # Build slider info with qualifiers
    slider_info = []
    for slider in relevant_sliders:
        qualifiers = slider.get("qualifiers", [])
        slider_info.append({
            "id": slider["id"],
            "label": slider.get("label", ""),
            "description": slider.get("description", ""),
            "default": slider.get("default", 0.5),
            "qualifiers": qualifiers,
            "qualifier_count": len(qualifiers),
        })

    return {
        "question": request.question,
        "relevant_factors": relevant_factors[:8],
        "suggested_sliders": slider_info,
        "slider_count": len(slider_info),
    }


# ── Step 2: Resolve qualifier answers → slider values ─────────────────


@router.post("/qualify")
async def resolve_qualifiers(
    answers: list[QualificationAnswer],
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Convert qualification answers into slider values.

    Each slider's value is the average of its qualifier answers.
    """
    await _check_license(user, db)

    slider_values = {}
    for answer in answers:
        slider = dag.get_slider(answer.slider_id)
        if not slider:
            raise HTTPException(
                status_code=404,
                detail=f"Slider '{answer.slider_id}' niet gevonden",
            )
        qualifiers = slider.get("qualifiers", [])
        if qualifiers and len(answer.answers) != len(qualifiers):
            raise HTTPException(
                status_code=422,
                detail=f"Slider '{answer.slider_id}' verwacht {len(qualifiers)} antwoorden",
            )
        for val in answer.answers:
            if not 0.0 <= val <= 1.0:
                raise HTTPException(
                    status_code=422,
                    detail="Antwoordwaarden moeten tussen 0 en 1 liggen",
                )
        if answer.answers:
            slider_values[answer.slider_id] = round(
                sum(answer.answers) / len(answer.answers), 4
            )
        else:
            slider_values[answer.slider_id] = slider.get("default", 0.5)

    return {"slider_values": slider_values, "count": len(slider_values)}


# ── Step 3: Simulate with qualified slider values ─────────────────────


@router.post("/simulate")
async def simulate_qualified(
    request: SimulateQualifiedRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Run simulation with the qualified slider values.

    Returns affected edges sorted by impact, with human-readable labels.
    """
    await _check_license(user, db)

    # Validate sliders
    for sid, val in request.slider_values.items():
        if not dag.get_slider(sid):
            raise HTTPException(status_code=404, detail=f"Slider '{sid}' niet gevonden")
        if not 0.0 <= val <= 1.0:
            raise HTTPException(status_code=422, detail="Waarden moeten tussen 0 en 1 liggen")

    edges = dag.get_all_relations()
    effects = simulate_sliders(dag.sliders, request.slider_values, edges)

    # Record usage
    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    # Build human-readable summary of top effects
    top_effects = []
    for e in effects[:15]:
        source_label = e.get("source_label", e.get("source", ""))
        target_label = e.get("target_label", e.get("target", ""))
        orig = e.get("original_strength", 0)
        adj = e.get("adjusted_strength", 0)
        diff = adj - orig
        direction = "versterkt" if diff > 0 else "verzwakt" if diff < 0 else "onveranderd"

        top_effects.append({
            "source": source_label,
            "target": target_label,
            "original": round(orig, 3),
            "adjusted": round(adj, 3),
            "change": round(diff, 3),
            "direction_nl": direction,
            "sliders": e.get("applied_sliders", []),
        })

    return {
        "question": request.question,
        "slider_values": request.slider_values,
        "effects": top_effects,
        "total_affected": len(effects),
    }


# ── Step 4: Generate advice using LLM ─────────────────────────────────


@router.post("/advice")
async def generate_advice(
    request: GenerateAdviceRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    dag: CausalDAG = Depends(get_dag),
):
    """Generate human-readable policy advice based on simulation results.

    Uses the LLM to translate simulation data into actionable recommendations
    at B2 language level, without technical jargon.
    """
    await _check_license(user, db)

    # S07-04: Resolve stored API key if sentinel is used
    api_key = request.api_key
    if api_key == "__stored__":
        api_key = await _resolve_stored_key(user.id, request.provider, db)
        if not api_key:
            raise HTTPException(
                status_code=422,
                detail="Geen opgeslagen API key gevonden voor deze provider. Voer een key in.",
            )

    # Build context from simulation
    effects_text = ""
    if request.effects:
        lines = []
        for e in request.effects[:10]:
            src = e.get("source", "?")
            tgt = e.get("target", "?")
            change = e.get("change", 0)
            direction = "positief" if change > 0 else "negatief" if change < 0 else "neutraal"
            lines.append(f"- {src} beïnvloedt {tgt} ({direction}, verandering: {change:+.3f})")
        effects_text = "\n".join(lines)

    slider_text = "\n".join(
        f"- {sid}: {val:.2f}" for sid, val in request.slider_values.items()
    )

    prompt = f"""Je bent een beleidsadviseur voor sportdeelname. Een beleidsmedewerker heeft
de volgende vraag gesteld:

"{request.question}"

De simulatie met het causale model geeft de volgende resultaten:

Sliderinstellingen:
{slider_text}

Belangrijkste effecten:
{effects_text if effects_text else "Geen significante effecten gevonden."}

Geef concreet en praktisch advies. Gebruik de volgende regels:
1. Schrijf op B2-taalniveau, vermijd jargon en technische termen
2. Zeg NIET "nodes", "edges", "factoren" of "variabelen" — gebruik gewone woorden
3. Beschrijf causale verbanden als "X beïnvloedt Y positief" of "X versterkt Z"
4. Geef 3-5 concrete aanbevelingen
5. Leg bij elke aanbeveling kort uit WAAROM dit werkt (het causale pad)
6. Sluit af met een korte samenvatting

Schrijf in het Nederlands."""

    messages = [
        {"role": "system", "content": "Je bent een vriendelijke maar professionele beleidsadviseur. Je geeft helder advies op basis van wetenschappelijk onderbouwde causale modellen."},
        {"role": "user", "content": prompt},
    ]

    connector = LLMConnector(request.provider, api_key, request.model)
    try:
        response = await connector.generate(messages)
    except LLMProviderError:
        raise HTTPException(
            status_code=502,
            detail="De AI-service kon het verzoek niet verwerken. Probeer het later opnieuw.",
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="De AI-service is tijdelijk niet bereikbaar.",
        )

    # Record additional query
    lm = LicenseManager(db)
    await lm.record_query(user.license_key)

    # Validate response against model
    validation = dag.validate_response_factors(response)

    return {
        "question": request.question,
        "advice": response,
        "validation": validation,
        "model_version": dag.version,
    }


# ── Helpers ────────────────────────────────────────────────────────────


async def _check_license(user: User, db: AsyncSession) -> None:
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

    try:
        license_obj = await lm.validate_license(user.license_key)
        if license_obj.tier == "free":
            usage = await lm.get_daily_usage(user.id)
            if usage["remaining"] <= 0:
                raise HTTPException(
                    status_code=403,
                    detail="Je dagelijkse gratis vragen zijn op. Upgrade naar een betaald account voor meer vragen.",
                )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="Licentie is ongeldig of verlopen")


async def _resolve_stored_key(user_id: int, provider: str, db: AsyncSession) -> str | None:
    """Retrieve and decrypt a stored API key for the given provider (S07-04)."""
    result = await db.execute(
        select(UserApiKey).where(
            UserApiKey.user_id == user_id,
            UserApiKey.provider == provider,
            UserApiKey.is_active == True,  # noqa: E712
        )
    )
    key_obj = result.scalar_one_or_none()
    if not key_obj:
        return None
    vault = KeyVault()
    return vault.decrypt(key_obj.encrypted_key)
