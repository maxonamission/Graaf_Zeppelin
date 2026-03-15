"""Tests for new features: factor search, response validation, conversations, export."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.core.auth import create_access_token, hash_password
from app.core.dag_engine import CausalDAG
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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _create_auth_cookies():
    """Helper: create license + user + stored key, return auth cookies."""
    stored_key_id = None
    async with async_session() as session:
        now = datetime.now(timezone.utc)
        lic = License(
            key="GZ-FEAT-TEST",
            organization="Feature Org",
            tier="professional",
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(days=365),
            queries_used=0,
        )
        session.add(lic)
        await session.commit()
        user = User(
            email="feature@example.com",
            hashed_password=hash_password("StrongPass123!"),
            full_name="Feature User",
            organization="Feature Org",
            license_key="GZ-FEAT-TEST",
        )
        session.add(user)
        await session.flush()

        vault = KeyVault()
        stored_key = UserApiKey(
            user_id=user.id,
            provider="openai",
            encrypted_key=vault.encrypt("sk-test"),
            key_hint="...test",
            is_active=True,
        )
        session.add(stored_key)
        await session.commit()
        stored_key_id = stored_key.id

    token = create_access_token({"sub": "feature@example.com"})
    return {"access_token": token}, stored_key_id


# ── Factor search tests ─────────────────────────────────────────────────


class TestFactorSearch:
    def test_find_relevant_factors(self):
        dag = app.state.dag
        results = dag.find_relevant_factors("deelname")
        assert len(results) > 0
        # Should find factors with "deelname" in label or definition
        labels = [r["label"].lower() for r in results]
        assert any("deelname" in l for l in labels)

    def test_find_factors_no_match(self):
        dag = app.state.dag
        results = dag.find_relevant_factors("xyznonsense")
        assert len(results) == 0

    def test_find_factors_short_terms_ignored(self):
        dag = app.state.dag
        results = dag.find_relevant_factors("de en")
        assert len(results) == 0

    def test_find_factors_max_results(self):
        dag = app.state.dag
        results = dag.find_relevant_factors("sport", max_results=3)
        assert len(results) <= 3


@pytest.mark.asyncio
class TestFactorSearchAPI:
    async def test_search_endpoint(self):
        cookies, _ = await _create_auth_cookies()
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get(
                "/api/graph/factors/search", params={"q": "deelname"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "factors" in data
            assert data["count"] > 0

    async def test_search_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/api/graph/factors/search", params={"q": "test"}
            )
            assert response.status_code == 401


# ── Response validation tests ────────────────────────────────────────────


class TestResponseValidation:
    def test_validate_response_with_known_factors(self):
        dag = app.state.dag
        # Get some actual factor labels
        factors = dag.get_all_factors()
        label = factors[0]["label"]
        result = dag.validate_response_factors(
            f"De factor {label} heeft een groot effect."
        )
        assert result["recognized_count"] >= 1
        assert any(f["label"] == label for f in result["recognized_factors"])

    def test_validate_response_no_factors(self):
        dag = app.state.dag
        result = dag.validate_response_factors("Dit bevat geen bekende factoren xyz.")
        assert result["recognized_count"] == 0

    def test_validate_response_model_count(self):
        dag = app.state.dag
        result = dag.validate_response_factors("test")
        assert result["model_factor_count"] == dag.graph.number_of_nodes()


# ── Validated query endpoint ─────────────────────────────────────────────


@pytest.mark.asyncio
class TestValidatedQuery:
    async def test_validated_query_with_mock_llm(self):
        cookies, stored_key_id = await _create_auth_cookies()
        mock_generate = AsyncMock(return_value="Deelname wordt beinvloed door vele factoren.")

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            with patch("app.core.llm_connector.LLMConnector.generate", mock_generate):
                response = await client.post(
                    "/api/reasoning/query/validated",
                    json={
                        "query": "Wat beinvloedt deelname aan sport?",
                        "provider": "openai",
                        "stored_key_id": stored_key_id,
                    },
                )
                assert response.status_code == 200
                data = response.json()
                assert "response" in data
                assert "validation" in data
                assert "auto_selected" in data
                assert data["auto_selected"] is True
                assert data["factors_used"] is not None


# ── Conversation tests ───────────────────────────────────────────────────


@pytest.mark.asyncio
class TestConversations:
    async def test_create_and_list_conversations(self):
        cookies, _ = await _create_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            # Create
            res = await client.post(
                "/api/conversations",
                json={"title": "Testgesprek"},
            )
            assert res.status_code == 200
            conv_id = res.json()["id"]

            # List
            list_res = await client.get("/api/conversations")
            assert list_res.status_code == 200
            data = list_res.json()
            assert data["count"] == 1
            assert data["conversations"][0]["title"] == "Testgesprek"

    async def test_add_and_get_messages(self):
        cookies, _ = await _create_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            # Create conversation
            res = await client.post(
                "/api/conversations",
                json={"title": "Met berichten"},
            )
            conv_id = res.json()["id"]

            # Add messages
            await client.post(
                f"/api/conversations/{conv_id}/messages",
                json={"role": "user", "content": "Hallo!"},
            )
            await client.post(
                f"/api/conversations/{conv_id}/messages",
                json={"role": "assistant", "content": "Welkom!"},
            )

            # Get conversation with messages
            get_res = await client.get(f"/api/conversations/{conv_id}")
            assert get_res.status_code == 200
            data = get_res.json()
            assert len(data["messages"]) == 2
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][1]["role"] == "assistant"

    async def test_delete_conversation(self):
        cookies, _ = await _create_auth_cookies()

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            res = await client.post(
                "/api/conversations",
                json={"title": "Te verwijderen"},
            )
            conv_id = res.json()["id"]

            del_res = await client.delete(f"/api/conversations/{conv_id}")
            assert del_res.status_code == 200

            get_res = await client.get(f"/api/conversations/{conv_id}")
            assert get_res.status_code == 404

    async def test_conversation_not_found(self):
        cookies, _ = await _create_auth_cookies()
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            res = await client.get("/api/conversations/99999")
            assert res.status_code == 404

    async def test_conversations_require_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.get("/api/conversations")
            assert res.status_code == 401


# ── Export tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestExport:
    async def test_export_markdown(self):
        cookies, _ = await _create_auth_cookies()
        dag = app.state.dag
        sliders = dag.get_sliders()
        if not sliders:
            pytest.skip("No sliders in model")

        slider_id = sliders[0]["id"]

        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.post(
                "/api/graph/export/markdown",
                json={"sliders": [{"id": slider_id, "value": 0.7}]},
            )
            assert response.status_code == 200
            assert "text/markdown" in response.headers["content-type"]
            body = response.text
            assert "Simulatierapport" in body
            assert "Sliderinstellingen" in body

    async def test_export_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/graph/export/markdown",
                json={"sliders": [{"id": "test", "value": 0.5}]},
            )
            assert response.status_code == 401
