# S12-03 — Voorbeeldvragen uit model-metadata laden

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: HOOG
**Geschatte omvang**: S
**Status:** ✅ Done

## Doel

De HTML-templates bevatten hardcoded voorbeeldvragen over sportdeelname. Deze moeten
dynamisch worden geladen uit het actieve model, zodat elk domein eigen voorbeeldvragen
kan meegeven.

## Bevindingen

| Locatie | Inhoud | Aantal |
|---------|--------|--------|
| `app/templates/reasoning.html:84-106` | Voorbeeldvragen chat ("Wat gebeurt er als we investeren in coaching...") | 6 stuks |
| `app/templates/wizard.html:54-67` | Voorbeeldvragen beleidsverkenner ("Hoe verhogen we sportdeelname...") | 3 stuks |
| `app/templates/home.html` | Introductietekst over sportdeelname | diverse |

## Acceptatiecriteria

- [ ] Voorbeeldvragen worden opgehaald uit model-metadata (veld `example_questions`) of een apart configuratiebestand
- [ ] Reasoning-template toont maximaal 6 voorbeeldvragen uit het model
- [ ] Wizard-template toont maximaal 3 voorbeeldvragen uit het model
- [ ] Fallback: als model geen voorbeeldvragen bevat, toon generieke placeholder ("Stel een vraag over het causale model...")
- [ ] API-endpoint `GET /api/graph/examples` levert de voorbeeldvragen als JSON
- [ ] Bestaande tests slagen

## Technische aanpak

1. Voeg `example_questions` array toe aan model-metadata JSON-schema:
   ```json
   "metadata": {
     "example_questions": {
       "reasoning": ["Vraag 1", "Vraag 2", ...],
       "wizard": ["Beleidsvraag 1", ...]
     }
   }
   ```
2. Voeg property `get_example_questions()` toe aan `CausalDAG`
3. Maak API-endpoint of inject in template-context via Jinja2
4. Vervang hardcoded HTML door `{% for q in example_questions %}`

## Afhankelijkheden

- S12-06 (model-metadata schema) voor de JSON-structuur
