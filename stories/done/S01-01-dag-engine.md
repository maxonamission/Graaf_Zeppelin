# S01-01: DAG Engine — model laden, queries, pad-analyse

**Epic:** EPIC-01 Causaal model laden & verkennen
**Status:** ✅ Done
**Module:** `app/core/dag_engine.py` (562 regels)

## Beschrijving

De DAG Engine laadt het extern aangeleverde causale model (JSON) en biedt
query-functionaliteit: factoren opvragen, relaties doorzoeken, paden vinden,
interventies simuleren.

## Wat is gebouwd

- Dual-schema ondersteuning (v1 + v2)
- Factor-queries per domein, cluster, status
- Pad-analyse (alle causale paden tussen twee factoren)
- Interventie-simulatie (effect propagatie door de graaf)
- NetworkX als graph-representatie

## Tests

33 tests in `tests/test_dag_engine.py` — alle slagen.
