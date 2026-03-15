# S12-04 — App-metadata configureerbaar maken

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: GEMIDDELD
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

App-titel, beschrijving en introductietekst zijn hardcoded voor "sportdeelname".
Deze moeten configureerbaar worden via `config.py` en/of model-metadata.

## Bevindingen

| Locatie | Hardcoded tekst |
|---------|----------------|
| `app/main.py:35` | `"Causaal redeneerplatform voor sportdeelname"` |
| `app/templates/home.html` | Introductietekst, domeinbeschrijving |
| `app/templates/base.html` | Mogelijk paginatitel |
| `app/templates/reasoning.html:80-82` | Intro "sportdeelname" |

## Acceptatiecriteria

- [ ] `config.py` bevat `domain_display_name: str` (default uit model-metadata)
- [ ] `main.py` app-beschrijving gebruikt config-waarde
- [ ] Templates tonen dynamische domeinnaam via Jinja2 context
- [ ] Home-pagina introductietekst is configureerbaar (uit model-metadata `summary.description` of config)
- [ ] Paginatitels bevatten domeinnaam dynamisch
- [ ] Bestaande tests slagen

## Technische aanpak

1. Voeg toe aan `config.py`:
   ```python
   domain_display_name: str = ""  # leeg = uit model-metadata
   ```
2. Bij app startup: als `domain_display_name` leeg, vul uit `dag.name`
3. Inject `domain_name` in Jinja2 template globals
4. Vervang hardcoded strings in templates

## Afhankelijkheden

- Geen (kan onafhankelijk worden opgepakt)
