"""Tests for Sprint 4: Graph viewer (S05-04), Paid tiers (S07-02/03),
Onboarding (S09-06), PostgreSQL (S10-02), Multi-model (S10-05)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.core.dag_engine import CausalDAG
from app.core.license_manager import LicenseTier, TIER_LIMITS
from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    """Authenticated test client with DAG loaded."""
    from app.db import engine
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        from app.db import async_session
        from app.models.license import License
        from app.models.user import User
        from app.core.auth import hash_password, create_access_token

        async with async_session() as session:
            lic = License(
                key="GZ-SPRINT4-TEST",
                organization="Sprint4 Org",
                tier="basis",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=365),
                queries_used=0,
            )
            session.add(lic)
            user = User(
                email="sprint4@test.nl",
                hashed_password=hash_password("StrongPass123!"),
                full_name="Sprint4 User",
                organization="Sprint4 Org",
                license_key="GZ-SPRINT4-TEST",
                role="admin",
            )
            session.add(user)
            await session.commit()

        token = create_access_token({"sub": "sprint4@test.nl"})
        c.cookies.set("access_token", token)
        yield c

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ── S05-04: Graph viewer improvements ────────────────────────────────


@pytest.mark.anyio
async def test_graph_viewer_page_loads(client):
    """S05-04: Graph viewer page should load with model selector."""
    res = await client.get("/graph")
    assert res.status_code == 200
    assert "model-selector" in res.text
    assert "domain-legend" in res.text
    assert "graph-tooltip" in res.text


@pytest.mark.anyio
async def test_domains_api_returns_data(client):
    """S05-04: Domains API provides data for color-coding."""
    res = await client.get("/api/graph/domains")
    assert res.status_code == 200
    data = res.json()
    assert "domains" in data


# ── S07-02: Paid account comparison ──────────────────────────────────


@pytest.mark.anyio
async def test_license_page_shows_tier_comparison(client):
    """S07-02: License page should show both account options."""
    res = await client.get("/license")
    assert res.status_code == 200
    html = res.text
    assert "Optie A" in html
    assert "Optie B" in html
    assert "BYOK" in html or "Eigen LLM" in html


class TestTierConfiguration:
    def test_all_tiers_defined(self):
        """S07-02: All tiers (free, basis, professional, enterprise, byok) exist."""
        assert LicenseTier.FREE in TIER_LIMITS
        assert LicenseTier.BASIS in TIER_LIMITS
        assert LicenseTier.PROFESSIONAL in TIER_LIMITS
        assert LicenseTier.ENTERPRISE in TIER_LIMITS
        assert LicenseTier.BYOK in TIER_LIMITS


# ── S07-03: Credits system ───────────────────────────────────────────


@pytest.mark.anyio
async def test_credits_status_endpoint(client):
    """S07-03: Credits status should return usage and warning level."""
    res = await client.get("/api/license/credits/status")
    assert res.status_code == 200
    data = res.json()
    assert "queries_used" in data
    assert "queries_limit" in data
    assert "percentage" in data
    assert "warning" in data


@pytest.mark.anyio
async def test_credits_topup_endpoint(client):
    """S07-03: Top-up should add credits to the license."""
    # First use some queries
    res = await client.get("/api/license/credits/status")
    initial = res.json()

    # Top up
    res = await client.post(
        "/api/license/credits/topup",
        json={"amount": 10},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["credits_added"] == 10


@pytest.mark.anyio
async def test_credits_topup_invalid_amount(client):
    """S07-03: Top-up with invalid amount should fail."""
    res = await client.post(
        "/api/license/credits/topup",
        json={"amount": 0},
    )
    assert res.status_code == 422


# ── S09-06: Onboarding ──────────────────────────────────────────────


@pytest.mark.anyio
async def test_onboarding_status(client):
    """S09-06: Onboarding status should be available."""
    res = await client.get("/api/auth/onboarding/status")
    assert res.status_code == 200
    data = res.json()
    assert "needs_onboarding" in data


@pytest.mark.anyio
async def test_onboarding_complete(client):
    """S09-06: User can mark onboarding as complete."""
    # Should need onboarding initially
    res = await client.get("/api/auth/onboarding/status")
    data = res.json()
    assert data["needs_onboarding"] is True

    # Complete it
    res = await client.post("/api/auth/onboarding/complete")
    assert res.status_code == 200

    # Should no longer need onboarding
    res = await client.get("/api/auth/onboarding/status")
    data = res.json()
    assert data["needs_onboarding"] is False


@pytest.mark.anyio
async def test_dashboard_shows_onboarding(client):
    """S09-06: Dashboard should include onboarding overlay."""
    res = await client.get("/dashboard")
    assert res.status_code == 200
    assert "onboarding-overlay" in res.text
    assert "Welkom bij Graaf Zeppelin" in res.text


# ── S10-02: PostgreSQL config ────────────────────────────────────────


class TestPostgreSQLConfig:
    def test_default_is_sqlite(self):
        """S10-02: Default database should be SQLite for development."""
        assert settings.is_sqlite
        assert "sqlite" in settings.database_url

    def test_is_sqlite_property(self):
        """S10-02: is_sqlite property works correctly."""
        assert settings.is_sqlite is True


def test_alembic_ini_exists():
    """S10-02: Alembic config should exist."""
    from pathlib import Path
    assert Path("alembic.ini").exists()
    assert Path("alembic/env.py").exists()


def test_migration_script_exists():
    """S10-02: SQLite to PostgreSQL migration script should exist."""
    from pathlib import Path
    assert Path("scripts/migrate_sqlite_to_pg.py").exists()


# ── S10-05: Multi-model support ──────────────────────────────────────


@pytest.mark.anyio
async def test_list_models(client):
    """S10-05: Models API should list available models."""
    res = await client.get("/api/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert data["count"] >= 1
    # Should include the default sportdeelname model
    model_ids = [m["id"] for m in data["models"]]
    assert any("sportdeelname" in mid for mid in model_ids)


@pytest.mark.anyio
async def test_current_model(client):
    """S10-05: Current model endpoint should return active model info."""
    res = await client.get("/api/models/current")
    assert res.status_code == 200
    data = res.json()
    assert "model_id" in data
    assert "name" in data
    assert "num_factors" in data


@pytest.mark.anyio
async def test_switch_model(client):
    """S10-05: Should be able to switch between models."""
    # List models first
    res = await client.get("/api/models")
    models = res.json()["models"]

    if len(models) < 2:
        pytest.skip("Need at least 2 models to test switching")

    # Switch to another model
    other = models[1]["id"]
    res = await client.post(
        "/api/models/switch",
        json={"model_id": other},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["switched"] is True
    assert data["model_id"] == other

    # Verify current model changed
    res = await client.get("/api/models/current")
    assert res.json()["model_id"] == other

    # Switch back
    await client.post(
        "/api/models/switch",
        json={"model_id": models[0]["id"]},
    )


@pytest.mark.anyio
async def test_switch_nonexistent_model(client):
    """S10-05: Switching to non-existent model should 404."""
    res = await client.post(
        "/api/models/switch",
        json={"model_id": "nonexistent_model_xyz"},
    )
    assert res.status_code == 404
