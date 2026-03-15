# S11-05 — Geautomatiseerde security checks (CI/herhaalbaar)

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: LAAG — plannen voor toekomstige sprint
**Geschatte omvang**: S
**Status:** ✅ Afgerond

## Doel

Security checks automatiseren zodat nieuwe kwetsbaarheden vroeg ontdekt worden, zonder handmatige audit.

## Acceptatiecriteria

- [x] `bandit` (Python SAST) draait als onderdeel van CI (GitHub Actions workflow)
- [x] `pip-audit` controleert dependencies op bekende CVE's (GitHub Actions workflow)
- [x] Resultaten rapporteren in JSON-formaat in `reports/` (uploaded als artifact)
- [x] Kwartaalijkse dependency-update via cron schedule in CI
- [x] Checklist-template voor security review bij nieuwe features

## Tooling

```bash
# Installatie (eenmalig)
pip install bandit pip-audit semgrep

# Draaien
bandit -r app/ -f json -o reports/bandit.json
pip-audit --format json --output reports/pip-audit.json
semgrep --config "p/owasp-top-ten" app/
```

## Checklist bij nieuwe feature (template)

```markdown
### Security checklist — [feature naam]

- [ ] Input-validatie op alle user-input (max lengte, type, format)
- [ ] Authenticatie vereist op endpoints
- [ ] Autorisatie/eigendomscontrole aanwezig
- [ ] Geen gevoelige data in API-responses of logs
- [ ] Rate limiting op resource-intensieve endpoints
- [ ] CSRF-bescherming op state-changing routes
- [ ] Tests voor ongeautoriseerde toegang (403/401)
```

## Herhaalbaar

Dit is per definitie een herhaalbare story — elke keer opnieuw uitvoerbaar.
