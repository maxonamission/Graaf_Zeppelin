# S07-01: Gratis vragen

**Epic:** EPIC-07 Businessmodel & toegang
**Status:** ✅ Done
**Prioriteit:** Hoog

## User Story

**Als** gratis gebruiker
**Wil ik** 1-2 vragen per dag kunnen stellen
**Zodat** ik de tool kan uitproberen voordat ik een licentie koop

## Acceptatiecriteria

- [x] DailyUsage model trackt dagelijks gebruik per gebruiker
- [x] FREE_DAILY_LIMIT = 2 vragen per dag
- [x] Quota wordt geenforced in reasoning en wizard API
- [x] Gebruikersvriendelijke foutmelding bij limiet bereikt
- [x] Free-tier banner op dashboard en reasoning-pagina
- [x] Banner wordt bijgewerkt na elke succesvolle query

## Technische details

- `app/models/daily_usage.py` — DailyUsage model
- `app/core/license_manager.py` — get_daily_usage(), record_free_query()
- `app/api/reasoning.py` — _check_license_and_quota() enforcing
- `app/api/wizard.py` — _check_license() updated met free-tier check
- `app/templates/dashboard.html`, `reasoning.html` — UI banners
