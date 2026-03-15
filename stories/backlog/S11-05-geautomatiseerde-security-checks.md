# S11-05 — Geautomatiseerde security checks (CI/herhaalbaar)

**Epic**: EPIC-11 Beveiliging
**Prioriteit**: LAAG — plannen voor toekomstige sprint
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

Security checks automatiseren zodat nieuwe kwetsbaarheden vroeg ontdekt worden, zonder handmatige audit.

## Acceptatiecriteria

- [ ] `bandit` (Python SAST) draait als onderdeel van test-suite of CI ❌ geïnstalleerd maar niet geautomatiseerd
- [ ] `pip-audit` controleert dependencies op bekende CVE's ❌ beschikbaar maar niet geautomatiseerd
- [ ] Resultaten rapporteren in JSON-formaat in `reports/` ❌ reports/ map bestaat niet
- [ ] Minimaal kwartaalijkse dependency-update ❌ geen schema
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
