# S11-04 — Beveiligingslogging & monitoring

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: GEMIDDELD — binnen 30 dagen na launch
**Geschatte omvang**: S
**Status:** ✅ Afgerond

## Doel

Beveiligingsrelevante events loggen zodat aanvallen detecteerbaar en traceerbaar zijn.

## Bevindingen die dit oplost

| # | Bevinding | Ernst | CWE |
|---|-----------|-------|-----|
| G3 | Informatielekken via foutmeldingen | GEMIDDELD | CWE-209 |
| G4 | Ontbrekende auditlogging | GEMIDDELD | CWE-778 |

## Acceptatiecriteria

- [x] Audit-logger apart van application-logger (`logging.getLogger("audit")`)
- [x] Gelogde events (minimaal):
  - ✅ Succesvolle en mislukte logins (e-mail, IP, tijdstip)
  - ✅ Registraties
  - ✅ Licentie-validatiefouten (audit_log in auth.py login)
  - ✅ API-key aanmaken/verwijderen
  - ✅ Credit-mutaties (topup)
  - ✅ Model-switches
  - ✅ Reasoning-queries (audit_log in reasoning.py, zonder inhoud)
- [x] Alle `str(e)` in HTTPException-responses vervangen door generieke berichten + server-side logging
- [x] Gedetailleerde errors alleen in server-logs (logger.exception/warning), niet naar client
- [x] Log-format: JSON met timestamp, event_type, user_id, IP, details
- [ ] Logbestanden niet wereldleesbaar (`chmod 640`) — N/A (deployment-afhankelijk)

## Technische notities

- `structlog` of standaard `logging` met JSON formatter
- Log-rotatie via `logrotate` of Docker logging driver
- Later uitbreidbaar met alerting (bijv. >10 mislukte logins/minuut)

## Herhaalbaar

Bij elke audit: controleer of nieuwe endpoints auditlogging hebben.
