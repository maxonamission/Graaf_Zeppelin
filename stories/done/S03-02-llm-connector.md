# S03-02: LLM Connector — OpenAI, Anthropic, BYOK

**Epic:** EPIC-03 AI-assistent (LLM-integratie)
**Status:** ✅ Done
**Module:** `app/core/llm_connector.py` (135 regels)

## Beschrijving

Multi-provider LLM client. Gebruiker koppelt eigen API key (BYOK).

## Wat is gebouwd

- OpenAI-integratie
- Anthropic-integratie
- BYOK (Bring Your Own Key) — gebruiker voert eigen key in
- Temperature 0.1 voor herhaalbare output
