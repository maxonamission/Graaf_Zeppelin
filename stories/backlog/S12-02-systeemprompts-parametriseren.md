# S12-02 — Systeemprompts parametriseren

**Epic**: EPIC-12 Multi-domein ondersteuning
**Prioriteit**: HOOG
**Geschatte omvang**: S
**Status:** 🔲 Backlog

## Doel

De systeemprompts bevatten hardcoded verwijzingen naar "sportdeelname". Deze moeten
dynamisch worden gevuld vanuit de model-metadata, zodat een ander model automatisch
de juiste domeinnaam, persona en context meekrijgt.

## Bevindingen

| Locatie | Hardcoded tekst |
|---------|----------------|
| `app/core/prompt_builder.py:15` | `"voor het domein sportdeelname"` |
| `app/api/wizard.py:250` | `"beleidsadviseur voor sportdeelname"` |
| `app/api/wizard.py:274` | `"expert in sportdeelname"` |

## Acceptatiecriteria

- [ ] `SYSTEM_PROMPT_TEMPLATE` in `prompt_builder.py` gebruikt `{domain_name}` in plaats van "sportdeelname"
- [ ] `PromptBuilder.__init__()` accepteert optioneel `domain_name` parameter, fallback naar model-metadata `project` veld
- [ ] Wizard-prompts in `wizard.py` halen domeinnaam op uit het actieve DAG-model (via `dag.name` of `dag.metadata`)
- [ ] Optioneel: model-metadata kan een `persona`-veld bevatten (bijv. "beleidsadviseur sportbeleid") dat in de prompt wordt gebruikt
- [ ] Bestaande tests slagen
- [ ] LLM-antwoorden benoemen het juiste domein (handmatige verificatie)

## Technische aanpak

1. Voeg `domain_name` property toe aan `CausalDAG` (uit `metadata.project` of apart veld)
2. Pas `PromptBuilder` aan: `__init__(self, dag, domain_name=None)`
3. Vervang hardcoded strings door f-string interpolatie
4. Pas `wizard.py` aan: haal domeinnaam uit `request.app.state.dag`

## Afhankelijkheden

- S12-06 (model-metadata schema) is wenselijk maar niet blokkerend — fallback op `dag.name`
