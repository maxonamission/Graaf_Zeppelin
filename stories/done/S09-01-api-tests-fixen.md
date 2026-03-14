# S09-01: API-tests fixen (async fixture)

**Epic:** EPIC-09 Stabiliteit & kwaliteit
**Status:** 🔲 Backlog
**Prioriteit:** Hoog

## Beschrijving

7 API-tests in `tests/test_api.py` falen door async fixture-incompatibiliteit.
De API-laag heeft hierdoor geen werkende testdekking.

## Technische details

- Probleem: pytest fixtures zijn sync, maar de FastAPI test client vereist async
- Oplossing: `pytest-asyncio` integreren of fixtures herschrijven
- Vereist: `pydantic[email]` als dependency

## Acceptatiecriteria

- [ ] Alle 7 API-tests slagen
- [ ] `pytest-asyncio` correct geconfigureerd
- [ ] CI draait alle tests inclusief API-tests
