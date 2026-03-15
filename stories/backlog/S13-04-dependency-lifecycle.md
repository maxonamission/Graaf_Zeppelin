# S13-04 — Dependency lifecycle management

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

Een proces inrichten zodat kwetsbaarheden in externe bibliotheken (dependencies) snel worden gedetecteerd en opgelost, ook nadat de applicatie in productie draait.

## Waarom dit belangrijk is

De collega noemt terecht dat "nieuwe kwetsbaarheden en aanvalstechnieken voortdurend ontstaan." De CI-pipeline (S11-05) draait pip-audit al per kwartaal, maar dat is niet frequent genoeg voor kritieke CVE's. Een kwetsbaarheid in een veelgebruikte bibliotheek (zoals log4shell in de Java-wereld) kan binnen uren actief worden misbruikt.

## Wat we al hebben

- `pip-audit` in CI (kwartaalbasis via S11-05)
- `bandit` + `semgrep` bij elke push
- Dependencies met minimale versienummers in `requirements.txt`

## Wat er mist

- Geen automatische notificatie bij nieuwe CVE's in onze dependencies
- Geen beleid voor hoe snel patches moeten worden doorgevoerd
- Dependencies zijn gepind op minimumversies (`>=`), niet op exacte versies — goed voor flexibiliteit, maar maakt builds minder reproduceerbaar

## Acceptatiecriteria

- [ ] GitHub Dependabot of vergelijkbaar ingeschakeld voor automatische CVE-meldingen
- [ ] SLA gedefinieerd: kritieke CVE's binnen 48 uur, hoge binnen 1 week
- [ ] `requirements.txt` aangevuld met `requirements-lock.txt` (exacte versies) voor reproduceerbare builds
- [ ] Kwartaalschema voor het bewust updaten van dependencies (niet alleen bij CVE's)
- [ ] Procedure gedocumenteerd in `docs/dependency-management.md`

## Afhankelijkheden

- S11-05 (geautomatiseerde scans) — al afgerond, wordt hiermee uitgebreid
