# S11-04 — Beveiligingslogging & monitoring

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: GEMIDDELD — binnen 30 dagen na launch
**Geschatte omvang**: S
**Status:** 🔶 Deels geïmplementeerd

## Doel

Beveiligingsrelevante events loggen zodat aanvallen detecteerbaar en traceerbaar zijn.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| G3 | Informatielekken via foutmeldingen | GEMIDDELD | CWE-209 |
| G4 | Ontbrekende auditlogging | GEMIDDELD | CWE-778 |

## Acceptatiecriteria

- [x] Audit-logger apart van application-logger (`logging.getLogger("audit")`)
- [ ] Gelogde events (minimaal): ⚠️ alleen login/registratie gelogd, rest ontbreekt
  - Succesvolle en mislukte logins (e-mail, IP, tijdstip)
  - Registraties
  - Licentie-validatiefouten
  - API-key aanmaken/verwijderen
  - Credit-mutaties (topup)
  - Model-switches
  - Reasoning-queries (zonder inhoud, wel user + tijdstip + model)
- [ ] Alle `str(e)` in HTTPException-responses vervangen door generieke berichten ⚠️ deels
- [ ] Gedetailleerde errors alleen in server-logs (niet naar client) ⚠️ deels
- [x] Log-format: JSON met timestamp, event_type, user_id, IP, details
- [ ] Logbestanden niet wereldleesbaar (`chmod 640`) — N/A (deployment-afhankelijk)

## Technische notities

- `structlog` of standaard `logging` met JSON formatter
- Log-rotatie via `logrotate` of Docker logging driver
- Later uitbreidbaar met alerting (bijv. >10 mislukte logins/minuut)

## Herhaalbaar

Bij elke audit: controleer of nieuwe endpoints auditlogging hebben.
