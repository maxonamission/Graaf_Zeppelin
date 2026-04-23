"""Tests for the FastAPI application and API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import create_access_token, hash_password
from app.db import engine, init_db
from app.main import app
from app.models.base import Base
from app.models.license import License
from app.models.user import User

from datetime import datetime, timedelta, timezone


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables and load graph model before each test, drop after."""
    from app.config import settings
    from app.core.dag_engine import CausalDAG

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Ensure DAG is loaded (lifespan doesn't run in test client)
    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def auth_cookie() -> dict:
    """Create a fake auth cookie for testing."""
    token = create_access_token({"sub": "test@example.com"})
    return {"access_token": token}


async def _create_licensed_user(db_session):
    """Helper: create a license and user in the database, return auth cookie dict."""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db import async_session

    async with async_session() as session:
        # Create license
        now = datetime.now(timezone.utc)
        lic = License(
            key="GZ-TEST-0001",
            organization="Test Org",
            tier="basis",
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(days=365),
            queries_used=0,
        )
        session.add(lic)
        await session.commit()

        # Create user
        user = User(
            email="test@example.com",
            hashed_password=hash_password("StrongPass123!"),
            full_name="Test User",
            organization="Test Org",
            license_key="GZ-TEST-0001",
        )
        session.add(user)
        await session.commit()

    token = create_access_token({"sub": "test@example.com"})
    return {"access_token": token}


@pytest.mark.asyncio
class TestPublicPages:
    async def test_home_page(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/")
            assert response.status_code == 200
            assert "Graaf Zeppelin" in response.text

    async def test_login_page(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/login")
            assert response.status_code == 200
            assert "Inloggen" in response.text

    async def test_register_page(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/register")
            assert response.status_code == 200
            assert "Registreren" in response.text


@pytest.mark.asyncio
class TestProtectedPages:
    async def test_dashboard_redirects_without_login(self):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get("/dashboard")
            assert response.status_code == 307

    async def test_graph_redirects_without_login(self):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get("/graph")
            assert response.status_code == 307

    async def test_reasoning_redirects_without_login(self):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get("/reasoning")
            assert response.status_code == 307


@pytest.mark.asyncio
class TestGraphAPI:
    async def test_graph_summary_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/graph/summary")
            assert response.status_code == 401

    async def test_graph_factors_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/graph/factors")
            assert response.status_code == 401

    async def test_graph_sliders_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/api/graph/sliders")
            assert response.status_code == 401

    async def test_graph_summary_with_auth(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/summary")
            assert response.status_code == 200
            data = response.json()
            assert "num_factors" in data
            assert "num_relations" in data

    async def test_graph_factors_with_auth(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/factors")
            assert response.status_code == 200
            data = response.json()
            assert "factors" in data
            assert "count" in data
            assert data["count"] > 0

    async def test_graph_domains_with_auth(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/domains")
            assert response.status_code == 200
            data = response.json()
            assert "domains" in data

    async def test_graph_sliders_with_auth(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/sliders")
            assert response.status_code == 200
            data = response.json()
            assert "sliders" in data
            assert data["count"] > 0

    async def test_graph_factor_not_found(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/factors/nonexistent")
            assert response.status_code == 404

    async def test_graph_relations_with_auth(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/relations")
            assert response.status_code == 200
            data = response.json()
            assert "relations" in data
            assert data["count"] > 0


@pytest.mark.asyncio
class TestSliderAPI:
    async def test_slider_qualify_relevant(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get(
                "/api/graph/sliders/qualify/relevant",
                params={"factor_ids": "UIT-L0-001"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "sliders" in data

    async def test_slider_qualify_no_factor(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get(
                "/api/graph/sliders/qualify/relevant",
                params={"factor_ids": "nonexistent_factor"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["count"] == 0

    async def test_slider_not_found(self):
        cookies = await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
            cookies=cookies,
        ) as client:
            response = await client.get("/api/graph/sliders/nonexistent")
            assert response.status_code == 404


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_login_invalid_credentials(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={"email": "nobody@example.com", "password": "wrong"},
            )
            assert response.status_code == 401

    async def test_login_valid_credentials(self):
        await _create_licensed_user(None)
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/auth/login",
                json={"email": "test@example.com", "password": "StrongPass123!"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["token_type"] == "bearer"
            # Token is now in httponly cookie, not response body
            assert "access_token" in response.cookies


@pytest.mark.asyncio
class TestReasoningAPI:
    async def test_reasoning_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/reasoning/query",
                json={
                    "query": "test",
                    "provider": "openai",
                    "stored_key_id": 1,
                },
            )
            assert response.status_code == 401

    async def test_intervene_requires_auth(self):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/api/reasoning/intervene",
                json={
                    "factor_id": "UIT-L0-001",
                    "change": 0.2,
                    "provider": "openai",
                    "stored_key_id": 1,
                },
            )
            assert response.status_code == 401
