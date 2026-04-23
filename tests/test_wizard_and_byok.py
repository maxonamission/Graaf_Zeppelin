"""Tests for Wizard API (S05-01/02/03), Dashboard (S05-05),
Free quota (S07-01), and BYOK (S07-04)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.key_vault import KeyVault
from app.core.license_manager import FREE_DAILY_LIMIT, LicenseTier
from app.main import app

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def anyio_backend():
    return "asyncio"


# ── Key Vault tests (S07-04) ─────────────────────────────────────────


class TestKeyVault:
    def test_encrypt_decrypt_roundtrip(self):
        vault = KeyVault()
        secret = "sk-test-1234567890abcdef"
        encrypted = vault.encrypt(secret)
        assert encrypted != secret
        decrypted = vault.decrypt(encrypted)
        assert decrypted == secret

    def test_different_inputs_produce_different_outputs(self):
        vault = KeyVault()
        enc1 = vault.encrypt("key-one")
        enc2 = vault.encrypt("key-two")
        assert enc1 != enc2

    def test_encrypted_key_is_not_plaintext(self):
        vault = KeyVault()
        secret = "sk-supersecret-key-12345"
        encrypted = vault.encrypt(secret)
        assert "supersecret" not in encrypted


# ── License Manager extensions (S07-01, S07-04) ──────────────────────


class TestLicenseTiers:
    def test_free_tier_exists(self):
        assert LicenseTier.FREE == "free"

    def test_byok_tier_exists(self):
        assert LicenseTier.BYOK == "byok"

    def test_free_tier_has_daily_limit(self):
        from app.core.license_manager import TIER_LIMITS

        limits = TIER_LIMITS[LicenseTier.FREE]
        assert "daily_limit" in limits
        assert limits["daily_limit"] == FREE_DAILY_LIMIT

    def test_byok_tier_has_high_query_limit(self):
        from app.core.license_manager import TIER_LIMITS

        limits = TIER_LIMITS[LicenseTier.BYOK]
        assert limits["queries_per_month"] >= 100000


# ── Wizard API tests (S05-01/02/03) ──────────────────────────────────


@pytest.fixture
async def authenticated_client(tmp_path):
    """Create an authenticated client with a test user and license."""
    from app.config import settings
    from app.core.dag_engine import CausalDAG
    from app.db import engine
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Ensure DAG is loaded (lifespan doesn't run in test client)
    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create license
        from app.core.auth import create_access_token, hash_password
        from app.db import async_session
        from app.models.license import License
        from app.models.user import User

        async with async_session() as session:
            lic = License(
                key="GZ-TEST-WIZARD",
                organization="Test Org",
                tier="basis",
                is_active=True,
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=365),
                queries_used=0,
            )
            session.add(lic)
            user = User(
                email="wizard@test.nl",
                hashed_password=hash_password("StrongPass123!"),
                full_name="Test Wizard",
                organization="Test Org",
                license_key="GZ-TEST-WIZARD",
            )
            session.add(user)
            await session.commit()

        token = create_access_token({"sub": "wizard@test.nl"})
        client.cookies.set("access_token", token)
        yield client

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.anyio
async def test_wizard_analyse_endpoint(authenticated_client):
    """S05-01: Analyse endpoint should return relevant sliders."""
    res = await authenticated_client.post(
        "/api/wizard/analyse",
        json={"question": "Hoe verhogen we sportdeelname?"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "suggested_sliders" in data
    assert "relevant_factors" in data
    assert data["question"] == "Hoe verhogen we sportdeelname?"


@pytest.mark.anyio
async def test_wizard_qualify_endpoint(authenticated_client):
    """S05-02: Qualify endpoint should convert answers to slider values."""
    # First get slider IDs via analyse
    res = await authenticated_client.post(
        "/api/wizard/analyse",
        json={"question": "sportdeelname"},
    )
    data = res.json()
    sliders = data["suggested_sliders"]

    if not sliders:
        pytest.skip("No sliders found in model")

    # Build qualification answers
    answers = []
    for s in sliders[:2]:
        qualifiers = s.get("qualifiers", [])
        if qualifiers:
            answers.append(
                {
                    "slider_id": s["id"],
                    "answers": [0.5] * len(qualifiers),
                }
            )
        else:
            answers.append(
                {
                    "slider_id": s["id"],
                    "answers": [0.5],
                }
            )

    if not answers:
        pytest.skip("No qualifiable sliders")

    res = await authenticated_client.post(
        "/api/wizard/qualify",
        json=answers,
    )
    assert res.status_code == 200
    data = res.json()
    assert "slider_values" in data


@pytest.mark.anyio
async def test_wizard_simulate_endpoint(authenticated_client):
    """S05-03: Simulate endpoint should return effects."""
    # Get sliders first
    res = await authenticated_client.post(
        "/api/wizard/analyse",
        json={"question": "sportdeelname"},
    )
    sliders = res.json()["suggested_sliders"]

    if not sliders:
        pytest.skip("No sliders found")

    slider_values = {s["id"]: 0.7 for s in sliders[:2]}

    res = await authenticated_client.post(
        "/api/wizard/simulate",
        json={
            "question": "Hoe verhogen we sportdeelname?",
            "slider_values": slider_values,
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "effects" in data
    assert "total_affected" in data


# ── Dashboard tests (S05-05) ─────────────────────────────────────────


@pytest.mark.anyio
async def test_dashboard_page_loads(authenticated_client):
    """S05-05: Dashboard should load with quick links."""
    res = await authenticated_client.get("/dashboard")
    assert res.status_code == 200
    html = res.text
    assert "Snel aan de slag" in html
    assert "/verkenner" in html
    assert "Verken beleid" in html


@pytest.mark.anyio
async def test_wizard_page_loads(authenticated_client):
    """S05-01: Wizard page should be accessible."""
    res = await authenticated_client.get("/verkenner")
    assert res.status_code == 200
    assert "Beleidsverkenner" in res.text
    assert "Beleidsvraag" in res.text


# ── Free quota tests (S07-01) ────────────────────────────────────────


@pytest.mark.anyio
async def test_free_quota_endpoint(authenticated_client):
    """S07-01: Free quota endpoint should return usage info."""
    res = await authenticated_client.get("/api/license/free-quota")
    assert res.status_code == 200
    data = res.json()
    # Authenticated user with basis license is not free tier
    assert "is_free_tier" in data


# ── BYOK API key management tests (S07-04) ───────────────────────────


@pytest.fixture
async def byok_client(tmp_path):
    """Create an authenticated BYOK-tier client."""
    from app.config import settings
    from app.core.dag_engine import CausalDAG
    from app.db import engine
    from app.models.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        from app.core.auth import create_access_token, hash_password
        from app.db import async_session
        from app.models.license import License
        from app.models.user import User

        async with async_session() as session:
            lic = License(
                key="GZ-BYOK-TEST",
                organization="BYOK Org",
                tier="byok",
                is_active=True,
                created_at=datetime.now(UTC),
                expires_at=datetime.now(UTC) + timedelta(days=365),
                queries_used=0,
            )
            session.add(lic)
            user = User(
                email="byok@test.nl",
                hashed_password=hash_password("StrongPass123!"),
                full_name="BYOK User",
                organization="BYOK Org",
                license_key="GZ-BYOK-TEST",
            )
            session.add(user)
            await session.commit()

        token = create_access_token({"sub": "byok@test.nl"})
        client.cookies.set("access_token", token)
        yield client

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.anyio
async def test_byok_store_api_key(byok_client):
    """S07-04: BYOK users can store API keys."""
    res = await byok_client.post(
        "/api/license/api-keys",
        json={"provider": "openai", "api_key": "sk-test-abcdefghijklmnop"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["stored"] is True
    assert data["hint"] == "...mnop"
    assert data["provider"] == "openai"


@pytest.mark.anyio
async def test_byok_list_api_keys(byok_client):
    """S07-04: BYOK users can list their stored keys (hints only)."""
    # Store a key first
    await byok_client.post(
        "/api/license/api-keys",
        json={"provider": "anthropic", "api_key": "sk-ant-test-xyz12345"},
    )

    res = await byok_client.get("/api/license/api-keys")
    assert res.status_code == 200
    data = res.json()
    assert len(data["keys"]) >= 1
    # Key should show hint, not the actual key
    key_info = data["keys"][0]
    assert "hint" in key_info
    assert "encrypted_key" not in key_info


@pytest.mark.anyio
async def test_non_byok_cannot_store_keys(authenticated_client):
    """S07-04: Non-BYOK users cannot store API keys."""
    res = await authenticated_client.post(
        "/api/license/api-keys",
        json={"provider": "openai", "api_key": "sk-test-abcdefghijklmnop"},
    )
    assert res.status_code == 403
