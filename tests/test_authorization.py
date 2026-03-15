"""Authorization tests — RBAC and resource isolation (S11-03)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core.auth import create_access_token, hash_password
from app.db import async_session, engine
from app.main import app
from app.models.base import Base
from app.models.conversation import Conversation
from app.models.license import License
from app.models.user import User, UserRole


@pytest.fixture(autouse=True)
async def setup_db():
    """Create/drop tables for each test."""
    from app.config import settings
    from app.core.dag_engine import CausalDAG
    from app.core.rate_limit import limiter

    limiter.reset()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    if not getattr(app.state, "dag", None):
        app.state.dag = CausalDAG.load(settings.graph_model_path)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def _create_user(email: str, role: str = "user") -> str:
    """Create a user and return a JWT token."""
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        lic = License(
            key=f"GZ-AUTH-{email[:5]}",
            organization="Auth Test Org",
            tier="basis",
            is_active=True,
            created_at=now,
            expires_at=now + timedelta(days=365),
            queries_used=0,
        )
        session.add(lic)
        user = User(
            email=email,
            hashed_password=hash_password("StrongPass123!"),
            full_name="Test User",
            organization="Auth Org",
            license_key=f"GZ-AUTH-{email[:5]}",
            role=role,
        )
        session.add(user)
        await session.commit()
    return create_access_token({"sub": email})


@pytest.mark.asyncio
class TestRoleBasedAccess:
    """Verify admin-only endpoints reject non-admin users."""

    async def test_switch_model_requires_admin(self):
        token = await _create_user("regular@test.nl", role="user")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/models/switch",
                json={"model_id": "sportdeelname_graph"},
                cookies={"access_token": token},
            )
            assert res.status_code == 403

    async def test_switch_model_allowed_for_admin(self):
        token = await _create_user("admin@test.nl", role="admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/models/switch",
                json={"model_id": "sportdeelname_graph"},
                cookies={"access_token": token},
            )
            assert res.status_code == 200

    async def test_credits_topup_requires_admin(self):
        token = await _create_user("user2@test.nl", role="user")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/license/credits/topup",
                json={"amount": 10},
                cookies={"access_token": token},
            )
            assert res.status_code == 403

    async def test_credits_topup_allowed_for_admin(self):
        token = await _create_user("admin2@test.nl", role="admin")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/license/credits/topup",
                json={"amount": 10},
                cookies={"access_token": token},
            )
            assert res.status_code == 200


@pytest.mark.asyncio
class TestResourceIsolation:
    """Verify users cannot access each other's resources."""

    async def test_cannot_see_other_users_conversations(self):
        token_a = await _create_user("alice@test.nl")
        token_b = await _create_user("bob@test.nl")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            # Alice creates a conversation
            res = await client.post(
                "/api/conversations",
                json={"title": "Alice's gesprek"},
                cookies={"access_token": token_a},
            )
            assert res.status_code == 200
            conv_id = res.json()["id"]

            # Bob tries to access it
            res = await client.get(
                f"/api/conversations/{conv_id}",
                cookies={"access_token": token_b},
            )
            assert res.status_code == 404

    async def test_cannot_delete_other_users_conversations(self):
        token_a = await _create_user("alice2@test.nl")
        token_b = await _create_user("bob2@test.nl")

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/conversations",
                json={"title": "Private"},
                cookies={"access_token": token_a},
            )
            conv_id = res.json()["id"]

            res = await client.delete(
                f"/api/conversations/{conv_id}",
                cookies={"access_token": token_b},
            )
            assert res.status_code == 404


@pytest.mark.asyncio
class TestConversationUUIDs:
    """Verify conversation IDs are UUIDs, not sequential integers."""

    async def test_conversation_id_is_uuid(self):
        import uuid

        token = await _create_user("uuidtest@test.nl")
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            res = await client.post(
                "/api/conversations",
                json={"title": "UUID test"},
                cookies={"access_token": token},
            )
            assert res.status_code == 200
            conv_id = res.json()["id"]

            # Verify it's a valid UUID
            parsed = uuid.UUID(conv_id)
            assert str(parsed) == conv_id


@pytest.mark.asyncio
class TestRoleEnum:
    """Verify the UserRole enum is properly defined."""

    def test_role_enum_values(self):
        assert UserRole.USER.value == "user"
        assert UserRole.ANALYST.value == "analyst"
        assert UserRole.ADMIN.value == "admin"

    def test_role_enum_membership(self):
        assert "user" in [r.value for r in UserRole]
        assert "analyst" in [r.value for r in UserRole]
        assert "admin" in [r.value for r in UserRole]
