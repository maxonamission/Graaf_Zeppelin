"""Tests for the LLMConnector — provider configuration and API call formatting."""

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.core.llm_connector import LLMConnector, LLMProviderError


class TestProviderConfig:
    def test_openai_provider(self):
        conn = LLMConnector("openai", "sk-test-key")
        assert conn.provider == "openai"
        assert conn.model == "gpt-4o"
        assert conn.api_key == "sk-test-key"

    def test_anthropic_provider(self):
        conn = LLMConnector("anthropic", "ant-test-key")
        assert conn.provider == "anthropic"
        assert conn.model == "claude-sonnet-4-20250514"
        assert conn.api_key == "ant-test-key"

    def test_custom_model(self):
        conn = LLMConnector("openai", "sk-key", model="gpt-4-turbo")
        assert conn.model == "gpt-4-turbo"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            LLMConnector("unknown", "key")

    def test_supported_providers_listed(self):
        try:
            LLMConnector("bad", "key")
        except ValueError as e:
            assert "openai" in str(e)
            assert "anthropic" in str(e)


@pytest.mark.asyncio
class TestOpenAICalls:
    async def test_openai_success(self):
        conn = LLMConnector("openai", "sk-test")
        mock_response = httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Test antwoord"}}]},
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await conn.generate([{"role": "user", "content": "Hallo"}])
            assert result == "Test antwoord"

    async def test_openai_api_error(self):
        conn = LLMConnector("openai", "sk-invalid")
        mock_response = httpx.Response(
            401,
            json={"error": {"message": "Invalid API key"}},
        )

        with (
            patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response),
            pytest.raises(LLMProviderError, match="OpenAI API error 401"),
        ):
            await conn.generate([{"role": "user", "content": "test"}])

    async def test_openai_rate_limit(self):
        conn = LLMConnector("openai", "sk-test")
        mock_response = httpx.Response(
            429,
            json={"error": {"message": "Rate limit exceeded"}},
        )

        with (
            patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response),
            pytest.raises(LLMProviderError, match="429"),
        ):
            await conn.generate([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
class TestAnthropicCalls:
    async def test_anthropic_success(self):
        conn = LLMConnector("anthropic", "ant-test")
        mock_response = httpx.Response(
            200,
            json={"content": [{"text": "Anthropic antwoord"}]},
        )

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            result = await conn.generate(
                [
                    {"role": "system", "content": "Je bent een assistent."},
                    {"role": "user", "content": "Hallo"},
                ]
            )
            assert result == "Anthropic antwoord"

    async def test_anthropic_separates_system_message(self):
        conn = LLMConnector("anthropic", "ant-test")

        captured_payload = {}

        async def mock_post(url, json, headers):
            captured_payload.update(json)
            return httpx.Response(
                200,
                json={"content": [{"text": "ok"}]},
            )

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            await conn.generate(
                [
                    {"role": "system", "content": "System prompt"},
                    {"role": "user", "content": "User msg"},
                ]
            )

        assert captured_payload["system"] == "System prompt"
        assert len(captured_payload["messages"]) == 1
        assert captured_payload["messages"][0]["role"] == "user"

    async def test_anthropic_api_error(self):
        conn = LLMConnector("anthropic", "ant-invalid")
        mock_response = httpx.Response(
            401,
            json={"error": {"message": "Invalid API key"}},
        )

        with (
            patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response),
            pytest.raises(LLMProviderError, match="Anthropic API error 401"),
        ):
            await conn.generate([{"role": "user", "content": "test"}])


@pytest.mark.asyncio
class TestGenerateParameters:
    async def test_custom_temperature_and_tokens(self):
        conn = LLMConnector("openai", "sk-test")

        captured_payload = {}

        async def mock_post(url, json, headers):
            captured_payload.update(json)
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok"}}]},
            )

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            await conn.generate(
                [{"role": "user", "content": "test"}],
                temperature=0.7,
                max_tokens=500,
            )

        assert captured_payload["temperature"] == 0.7
        assert captured_payload["max_tokens"] == 500
