# S02-03: Kwalificatievragen — technische infrastructuur

**Epic:** EPIC-02 Interventie-simulatie met sliders
**Status:** ✅ Done
**Module:** `data/models/sportdeelname_graph.json` (qualifiers veld)

## Beschrijving

Technische infrastructuur voor slider-kwalificatievragen: JSON-schema,
API-endpoints, relevantiefiltering. Inhoudelijke validatie staat in EPIC-08.

## Wat is gebouwd

- `qualifiers` veld in alle 8 sliders (2 vragen per slider, 16 totaal)
- Multiple-choice antwoorden met numerieke waarde-mapping (0–1)
- Relevantiefiltering op `related_nodes` en `primary_clusters`
- API-endpoints (zie S02-02)

## Referentie

Zie `docs/epic_slider_qualifiers.md` voor volledige technische context en
de 5 validatie-stories.
