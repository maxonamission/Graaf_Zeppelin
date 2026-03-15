# S11-03 — Autorisatie & toegangscontrole verbeteren

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: HOOG — vóór productie
**Geschatte omvang**: M
**Status:** 🔶 Deels geïmplementeerd

## Doel

Privilege escalation en ongeautoriseerde acties voorkomen door rolgebaseerde toegangscontrole (RBAC) en resource-isolatie.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| H3 | Credits topup zonder betaling of limiet | HOOG | CWE-269 |
| H4 | Model-switching beïnvloedt alle gebruikers | HOOG | CWE-269 |
| G5 | Sequentiële ID's (IDOR-risico) | GEMIDDELD | CWE-639 |

## Acceptatiecriteria

- [ ] Rolmodel geïmplementeerd: `user`, `analyst`, `admin` ⚠️ User.role bestaat maar geen enum, geen analyst-rol
- [x] `/api/models/switch` alleen toegankelijk voor `admin`
- [x] `/api/license/credits/topup` vereist admin-goedkeuring of betaalintegratie
  - Tijdelijke oplossing: admin-only endpoint + maximale top-up van 100 per transactie
- [ ] Model-selectie per sessie (niet globaal `app.state`), of per-user override ❌ nog globaal
- [ ] Conversatie-ID's zijn UUIDs in plaats van sequentiële integers ❌ nog Integer PK
- [x] API-key beheer: gebruiker kan alleen eigen keys zien/verwijderen
- [ ] Alle autorisatiecontroles ook in tests gedekt ⚠️ basistests aanwezig, maar niet dekkend

## Technische notities

- `User.role` veld toevoegen (Enum: user/analyst/admin)
- `require_role("admin")` dependency voor beschermde endpoints
- Model per sessie: session-variable of user-preference in database
- UUIDs: `import uuid; id = Column(UUID, default=uuid.uuid4)`

## Herhaalbaar

Bij elk nieuw endpoint dat data wijzigt:
1. Is er een eigendomscontrole?
2. Is er een rolcontrole?
3. Zijn ID's niet-voorspelbaar?
