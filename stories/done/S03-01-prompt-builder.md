# S03-01: Prompt Builder — 4 templates, 6 constraints, NL

**Epic:** EPIC-03 AI-assistent (LLM-integratie)
**Status:** ✅ Done
**Module:** `app/core/prompt_builder.py` (336 regels)

## Beschrijving

Vertaalt DAG-queries naar gestructureerde LLM-prompts in het Nederlands,
met 6 causale redeneerbeperkingen die het LLM dwingen binnen het model te blijven.

## Wat is gebouwd

- 4 prompttemplates (verkenning, interventie, vergelijking, uitleg)
- 6 constraints (geen nieuwe relaties verzinnen, pad volgen, epistemische terughoudendheid, etc.)
- Automatische context-injectie van relevante domeinen en factoren
- Nederlands als verplichte antwoordtaal

## Tests

7 tests in `tests/test_prompt_builder.py` — alle slagen.
