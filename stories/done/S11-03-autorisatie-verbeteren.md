# S11-03 — Autorisatie & toegangscontrole verbeteren

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: HOOG — vóór productie
**Geschatte omvang**: M
**Status:** ✅ Afgerond

## Doel

Privilege escalation en ongeautoriseerde acties voorkomen door rolgebaseerde toegangscontrole (RBAC) en resource-isolatie.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| H3 | Credits topup zonder betaling of limiet | HOOG | CWE-269 |
| H4 | Model-switching beïnvloedt alle gebruikers | HOOG | CWE-269 |
| G5 | Sequentiële ID's (IDOR-risico) | GEMIDDELD | CWE-639 |

## Acceptatiecriteria

- [x] Rolmodel geïmplementeerd: `UserRole` enum met `user`, `analyst`, `admin` + `require_role()` dependency
- [x] `/api/models/switch` alleen toegankelijk voor `admin` (via `require_role(UserRole.ADMIN)`)
- [x] `/api/license/credits/topup` vereist admin-goedkeuring (via `require_role(UserRole.ADMIN)`)
  - Tijdelijke oplossing: admin-only endpoint + maximale top-up van 100 per transactie
- [x] Model-selectie per user via `preferred_model` veld + `/api/models/prefer` endpoint + `get_user_dag` dependency
- [x] Conversatie-ID's zijn UUIDs (String(36) met uuid4 default)
- [x] API-key beheer: gebruiker kan alleen eigen keys zien/verwijderen
- [x] Autorisatiecontroles in tests (test_authorization.py: RBAC, resource isolation, UUID verificatie)

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
