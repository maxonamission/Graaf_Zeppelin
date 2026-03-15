# S05-05: Dashboard aanscherpen

**Epic:** EPIC-05 Begeleide beleidsverkenning
**Status:** Done
**Prioriteit:** Midden

## User Story

**Als** beleidsmedewerker
**Wil ik** een overzichtelijk dashboard met relevante informatie
**Zodat** ik snel kan navigeren naar mijn werk en het model kan begrijpen

## Acceptatiecriteria

- [x] Domeinoverzicht kaart met factortelling en kleurcodering
- [x] Recente verkenningen sectie met datum en advies-badge
- [x] Inklapbaar model-informatieblok
- [x] Nieuw-knop bij recente verkenningen
- [x] Domeinbalken tonen relatief aandeel

## Technische details

- `app/templates/dashboard.html` — Herschreven met domeinoverzicht, explorations
- Gebruikt /api/graph/domains en /api/explorations endpoints
