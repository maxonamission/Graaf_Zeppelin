"""Tests for the FastAPI application and API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.auth import create_access_token
from app.db import engine, init_db
from app.main import app
from app.models.base import Base


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test and drop after."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def auth_cookie() -> dict:
    """Create a fake auth cookie for testing."""
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
