# S03-03: Reasoning API — query & interventie endpoints

**Epic:** EPIC-03 AI-assistent (LLM-integratie)
**Status:** ✅ Done
**Module:** `app/api/reasoning.py` (118 regels)

## Beschrijving

REST endpoints voor LLM-redenering over het causale model.

## Wat is gebouwd

- `POST /api/reasoning/query` — stel een vraag over het model
- `POST /api/reasoning/intervene` — vraag advies over een interventie
- Automatische context-injectie uit de DAG
