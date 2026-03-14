# S02-02: Slider API — endpoints voor sliders, kwalificatie, simulatie

**Epic:** EPIC-02 Interventie-simulatie met sliders
**Status:** ✅ Done
**Module:** `app/api/graph.py`

## Beschrijving

REST endpoints voor de slider-functionaliteit: opvragen, kwalificeren,
simuleren.

## Wat is gebouwd

- `GET /api/graph/sliders` — alle beleidssliders met curvedefinities
- `GET /api/graph/sliders/{id}` — enkele slider
- `GET /api/graph/sliders/{id}/qualify` — kwalificatievragen per slider
- `GET /api/graph/sliders/qualify/relevant` — relevante sliders voor factoren
- `POST /api/graph/sliders/qualify` — antwoorden → sliderwaarden
- `POST /api/graph/simulate` — multi-slider simulatie
