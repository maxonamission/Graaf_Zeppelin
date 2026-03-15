# S05-01: Begeleide interventie-flow

**Epic:** EPIC-05 Begeleide beleidsverkenning
**Status:** ✅ Done
**Prioriteit:** Hoog

## User Story

**Als** beleidsmedewerker
**Wil ik** mijn beleidsverkenningen kunnen opslaan en later terugvinden
**Zodat** ik eerder uitgevoerde analyses kan hergebruiken en delen

## Acceptatiecriteria

- [x] Exploration model (DB tabel) voor opslaan van vraag, sliders, effecten en advies
- [x] API endpoints: POST/GET/DELETE /api/explorations
- [x] Opslaan-knop na stap 4 (advies)
- [x] Panel met opgeslagen verkenningen (laden/verwijderen)
- [x] Laden van eerdere verkenning herstelt de wizard-state (resultaten of advies)
- [x] Teller toont aantal opgeslagen verkenningen

## Technische details

- `app/models/exploration.py` — Exploration SQLAlchemy model
- `app/api/explorations.py` — CRUD endpoints
- `app/templates/wizard.html` — Opslaan/laden UI
- Router geregistreerd in `app/main.py`
