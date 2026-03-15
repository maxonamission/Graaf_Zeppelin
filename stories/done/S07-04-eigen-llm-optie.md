# S07-04: Eigen LLM-optie (BYOK)

**Epic:** EPIC-07 Businessmodel & toegang
**Status:** ✅ Done
**Prioriteit:** Midden

## User Story

**Als** BYOK-gebruiker
**Wil ik** mijn opgeslagen API key automatisch laten gebruiken
**Zodat** ik niet steeds mijn key hoef in te voeren

## Acceptatiecriteria

- [x] Opgeslagen API keys worden automatisch gedetecteerd
- [x] Groene indicator toont welke opgeslagen key wordt gebruikt
- [x] Gebruiker kan altijd een andere key invoeren
- [x] Backend resolvet __stored__ sentinel naar versleutelde key
- [x] Foutmelding als geen opgeslagen key beschikbaar is
- [x] Provider-wissel detecteert beschikbare keys

## Technische details

- `app/api/wizard.py` — _resolve_stored_key() + sentinel support
- `app/api/reasoning.py` — _resolve_api_key() + sentinel support
- `app/templates/wizard.html`, `reasoning.html` — Auto-fill UI
- `app/core/key_vault.py` — decrypt() voor key recovery
