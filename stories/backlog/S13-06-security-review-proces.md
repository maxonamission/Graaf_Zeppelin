# S13-06 — Structureel security review proces

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

Een herhaalbaar proces inrichten zodat beveiliging geen eenmalige actie is maar een doorlopend onderdeel van de ontwikkelcyclus.

## Waarom dit belangrijk is

De collega benadrukt dat OWASP/CWE een "goed vertrekpunt" is, maar dat "aanvullende maatregelen zoals code reviews essentieel zijn voor een volledige beveiligingsstrategie." Een beveiligingsaudit die één keer wordt uitgevoerd veroudert snel. Elke nieuwe feature, elke nieuwe dependency, elke configuratiewijziging kan nieuwe risico's introduceren.

## Wat we al hebben

- Eenmalige beveiligingsaudit (docs/beveiligingsaudit-v2.md)
- Geautomatiseerde scans in CI (bandit, pip-audit, semgrep)
- Herhalingsschema in de audit (bij major releases, nieuwe endpoints, etc.)

## Wat er mist

- Geen security checklist voor code reviews
- Geen periodieke herhaling van de handmatige audit
- Geen verantwoordelijke aangewezen voor beveiligingsonderwerpen

## Acceptatiecriteria

- [ ] Security checklist voor pull request reviews (bijv. "Heeft dit endpoint rate limiting? Is input gevalideerd? Wordt data ge-escaped in de template?")
- [ ] Jaarplanning: kwartaal-scan (geautomatiseerd), halfjaarlijkse handmatige review, jaarlijkse pentest
- [ ] Security champion aangewezen (teamlid dat beveiligingskwesties bewaakt)
- [ ] Checklist en planning opgeleverd als `docs/security-review-proces.md`
- [ ] Herhalingsschema uit beveiligingsaudit-v2.md geïntegreerd in dit proces

## Afhankelijkheden

- S13-01 (threat model) — levert input voor de checklist
- S13-03 (penetratietest) — eerste uitvoering van het jaarlijkse schema
