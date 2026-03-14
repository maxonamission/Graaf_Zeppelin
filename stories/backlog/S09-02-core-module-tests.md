# S09-02: Tests voor core modules

**Epic:** EPIC-09 Stabiliteit & kwaliteit
**Status:** 🔲 Backlog
**Prioriteit:** Hoog

## Beschrijving

Meerdere core modules missen dedicated tests:
- `core/llm_connector.py` — geen tests
- `core/license_manager.py` — geen tests
- `core/auth.py` — geen tests
- `core/release_manager.py` — geen tests

## Acceptatiecriteria

- [ ] LLM Connector: tests voor provider-selectie, error handling, mock API calls
- [ ] License Manager: tests voor tier-logica, quota-berekening, key-validatie
- [ ] Auth: tests voor JWT generatie/validatie, wachtwoordhashing
- [ ] Release Manager: tests voor versioning, migratieguide-generatie
