"""
LLM Connector — Multi-provider LLM client.

Supports OpenAI, Anthropic, and potentially local models.
Users connect their own API keys.
"""

from __future__ import annotations

from typing import Any

import httpx


class LLMProviderError(Exception):
    """Raised when an LLM provider returns an error."""


class LLMConnector:
    """Connects to LLM providers using user-supplied API keys."""

    PROVIDERS = {
        "openai": {
            "base_url": "https://api.openai.com/v1/chat/completions",
            "default_model": "gpt-4o",
            "auth_header": "Authorization",
            "auth_prefix": "Bearer ",
        },
        "anthropic": {
            "base_url": "https://api.anthropic.com/v1/messages",
            "default_model": "claude-sonnet-4-20250514",
            "auth_header": "x-api-key",
            "auth_prefix": "",
        },
    }

    def __init__(self, provider: str, api_key: str, model: str | None = None):
        if provider not in self.PROVIDERS:
            raise ValueError(
                f"Unknown provider '{provider}'. "
                f"Supported: {', '.join(self.PROVIDERS.keys())}"
            )
        self.provider = provider
        self.api_key = api_key
        self.config = self.PROVIDERS[provider]
        self.model = model or self.config["default_model"]

    async def generate(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        """Send messages to the LLM and return the response text.

        Uses low temperature by default for repeatable outputs.
        """
        if self.provider == "openai":
            return await self._call_openai(messages, temperature, max_tokens)
        elif self.provider == "anthropic":
            return await self._call_anthropic(messages, temperature, max_tokens)
        raise LLMProviderError(f"Provider '{self.provider}' not implemented")

    async def _call_openai(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        headers = {
            self.config["auth_header"]: f"{self.config['auth_prefix']}{self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.config["base_url"], json=payload, headers=headers
            )

        if response.status_code != 200:
            raise LLMProviderError(
                f"OpenAI API error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    async def _call_anthropic(
        self,
        messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
    ) -> str:
        # Anthropic uses a separate system parameter
        system_msg = ""
        user_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                user_messages.append(msg)

        headers = {
            self.config["auth_header"]: f"{self.config['auth_prefix']}{self.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if system_msg:
            payload["system"] = system_msg

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.config["base_url"], json=payload, headers=headers
            )

        if response.status_code != 200:
            raise LLMProviderError(
                f"Anthropic API error {response.status_code}: {response.text}"
            )

        data = response.json()
        return data["content"][0]["text"]
