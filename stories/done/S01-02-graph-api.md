# S01-02: Graph API — 12 REST endpoints

**Epic:** EPIC-01 Causaal model laden & verkennen
**Status:** ✅ Done
**Module:** `app/api/graph.py` (369 regels)

## Beschrijving

REST API endpoints voor het verkennen van het causale model: factoren,
relaties, domeinen, paden, sliders en simulatie.

## Wat is gebouwd

- `GET /api/graph/summary` — modeloverzicht
- `GET /api/graph/domains` — domeinen met tellingen
- `GET /api/graph/factors` — factoren (filter op domein/cluster/status)
- `GET /api/graph/factors/{id}` — factordetails met oorzaken/gevolgen
- `GET /api/graph/relations` — relaties (filter op polariteit/type)
- `GET /api/graph/paths/{source}/{target}` — causale paden
- `POST /api/graph/intervene` — interventie simuleren
- Slider endpoints (zie S02-02)
