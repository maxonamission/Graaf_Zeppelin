"""Integration tests — end-to-end flows through the API.

Tests the complete user journey: register → login → explore → simulate → reason.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import hash_password
from app.core.key_vault import KeyVault
from app.db import async_session, engine
from app.main import app
from app.models.base import Base
from app.models.license import License
from app.models.user import User
from app.models.user_api_key import UserApiKey


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables and load graph model before each test, drop after."""
    from app.config import settings
    from app.core.dag_engine import CausalDAG

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _seed_license():
    """Create a test license in the database."""
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        lic = License(
            key="GZ-INTEG-TEST",
            organization="Integration Org",
            tier="professional",
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(days=365),
            queries_used=0,
        )
        session.add(lic)
        await session.commit()


@pytest.mark.asyncio
class TestRegistrationLoginFlow:
    """Test: registration → login → receive token → access protected resource."""

    async def test_register_and_login(self):
        await _seed_license()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Register
            reg_response = await client.post(
                "/api/auth/register",
                json={
                    "email": "new@example.com",
                    "password": "strongpass123",
                    "full_name": "New User",
                    "organization": "Integration Org",
                    "license_key": "GZ-INTEG-TEST",
                },
            )
            assert reg_response.status_code == 200
            reg_data = reg_response.json()
            assert "access_token" in reg_data

            # Login with same credentials
            login_response = await client.post(
                "/api/auth/login",
                json={
                    "email": "new@example.com",
                    "password": "strongpass123",
                },
            )
            assert login_response.status_code == 200
            login_data = login_response.json()
            assert "access_token" in login_data

            # Access protected endpoint with token
            cookies = {"access_token": login_data["access_token"]}
            summary_response = await client.get(
                "/api/graph/summary", cookies=cookies
            )
            assert summary_response.status_code == 200
            assert "num_factors" in summary_response.json()

    async def test_register_duplicate_email(self):
        await _seed_license()

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            payload = {
                "email": "dupe@example.com",
                "password": "pass123",
                "full_name": "User",
                "organization": "Org",
                "license_key": "GZ-INTEG-TEST",
            }
            await client.post("/api/auth/register", json=payload)
            response = await client.post("/api/auth/register", json=payload)
            assert response.status_code == 400
            assert "al geregistreerd" in response.json()["detail"]

    async def test_register_invalid_license(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/register",
                json={
                    "email": "noone@example.com",
                    "password": "pass123",
                    "full_name": "User",
                    "organization": "Org",
                    "license_key": "INVALID-KEY",
                },
            )
            assert response.status_code == 400


@pytest.mark.asyncio
class TestModelExplorationFlow:
    """Test: login → load model → request factors → view details."""

    async def _get_auth_cookies(self):
        await _seed_license()
        async with async_session() as session:
            user = User(
                email="explorer@example.com",
                hashed_password=hash_password("pass123"),
                full_name="Explorer",
                organization="Org",
                license_key="GZ-INTEG-TEST",
            )
            session.add(user)
            await session.commit()

        from app.core.auth import create_access_token

        token = create_access_token({"sub": "explorer@example.com"})
        return {"access_token": token}

    async def test_explore_factors_and_details(self):
        cookies = await self._get_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            # List all factors
            factors_res = await client.get("/api/graph/factors")
            assert factors_res.status_code == 200
            factors = factors_res.json()["factors"]
            assert len(factors) > 0

            # Get details of the first factor
            first_id = factors[0]["id"]
            detail_res = await client.get(f"/api/graph/factors/{first_id}")
            assert detail_res.status_code == 200
            detail = detail_res.json()
            assert detail["id"] == first_id
            assert "label" in detail

    async def test_explore_domains(self):
        cookies = await self._get_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/domains")
            assert response.status_code == 200
            assert "domains" in response.json()

    async def test_explore_relations(self):
        cookies = await self._get_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/relations")
            assert response.status_code == 200
            data = response.json()
            assert data["count"] > 0


@pytest.mark.asyncio
class TestSliderSimulationFlow:
    """Test: qualify sliders → run simulation → receive results."""

    async def _get_auth_cookies(self):
        await _seed_license()
        async with async_session() as session:
            user = User(
                email="simulator@example.com",
                hashed_password=hash_password("pass123"),
                full_name="Simulator",
                organization="Org",
                license_key="GZ-INTEG-TEST",
            )
            session.add(user)
            await session.commit()

        from app.core.auth import create_access_token

        token = create_access_token({"sub": "simulator@example.com"})
        return {"access_token": token}

    async def test_full_slider_flow(self):
        cookies = await self._get_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            # 1. List sliders
            sliders_res = await client.get("/api/graph/sliders")
            assert sliders_res.status_code == 200
            sliders = sliders_res.json()["sliders"]
            assert len(sliders) > 0

            first_slider = sliders[0]
            slider_id = first_slider["id"]

            # 2. Get qualifier questions for a slider
            qual_res = await client.get(f"/api/graph/sliders/{slider_id}/qualify")
            assert qual_res.status_code == 200
            qualifiers = qual_res.json()["qualifiers"]

            # 3. Submit qualifier answers
            answers = [0.5] * len(qualifiers)
            qualify_res = await client.post(
                "/api/graph/sliders/qualify",
                json={
                    "responses": [
                        {"slider_id": slider_id, "answers": answers}
                    ]
                },
            )
            assert qualify_res.status_code == 200
            slider_values = qualify_res.json()["slider_values"]
            assert slider_id in slider_values

            # 4. Run simulation with computed slider values
            sim_res = await client.post(
                "/api/graph/simulate",
                json={
                    "sliders": [
                        {"id": slider_id, "value": slider_values[slider_id]}
                    ]
                },
            )
            assert sim_res.status_code == 200
            assert "affected_edges" in sim_res.json()

    async def test_simulation_with_invalid_slider(self):
        cookies = await self._get_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.post(
                "/api/graph/simulate",
                json={"sliders": [{"id": "nonexistent", "value": 0.5}]},
            )
            assert response.status_code == 404


@pytest.mark.asyncio
class TestReasoningFlow:
    """Test: ask AI question → receive answer (with mock LLM)."""

    async def _get_auth_cookies(self):
        await _seed_license()
        async with async_session() as session:
            user = User(
                email="reasoner@example.com",
                hashed_password=hash_password("pass123"),
                full_name="Reasoner",
                organization="Org",
                license_key="GZ-INTEG-TEST",
            )
            session.add(user)
            await session.flush()

            vault = KeyVault()
            stored_key = UserApiKey(
                user_id=user.id,
                provider="openai",
                encrypted_key=vault.encrypt("sk-test-key"),
                key_hint="...key",
                is_active=True,
            )
            session.add(stored_key)
            await session.commit()
            self._stored_key_id = stored_key.id

        from app.core.auth import create_access_token

        token = create_access_token({"sub": "reasoner@example.com"})
        return {"access_token": token}

    async def test_reasoning_query_with_mock_llm(self):
        cookies = await self._get_auth_cookies()

        mock_generate = AsyncMock(
            return_value="Coaching heeft een positief effect op sportdeelname."
        )

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            with patch(
                "app.core.llm_connector.LLMConnector.generate",
                mock_generate,
            ):
                response = await client.post(
                    "/api/reasoning/query",
                    json={
                        "query": "Wat is het effect van coaching op sportdeelname?",
                        "provider": "openai",
                        "stored_key_id": self._stored_key_id,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert "coaching" in data["response"].lower()

    async def test_reasoning_intervention_with_mock_llm(self):
        cookies = await self._get_auth_cookies()

        mock_generate = AsyncMock(
            return_value="Een toename in coaching kwaliteit leidt tot betere sportdeelname."
        )

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            with patch(
                "app.core.llm_connector.LLMConnector.generate",
                mock_generate,
            ):
                response = await client.post(
                    "/api/reasoning/intervene",
                    json={
                        "factor_id": "N001",
                        "change": 0.3,
                        "description": "Meer investering in coaching",
                        "provider": "openai",
                        "stored_key_id": self._stored_key_id,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert "analysis" in data
                assert "simulation" in data
