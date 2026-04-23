# S14-07: Schema-evolutie documenteren als methodologie-bijdrage (GZ-07)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Laag
**Bron:** `docs/actieplan-os.md` §GZ-07

## Doel

De v1→v2-schemamigratie die Zeppelin al heeft doorgemaakt expliciet documenteren als
voorbeeld voor andere graph-projecten. Bijdrage aan de gedeelde methodologie.

## Context

Olympus heeft (nog) geen schema-migratie achter de rug; Zeppelin wel. De kennis hoe
je dat doet — welke stappen, welke valkuilen, hoe je backward-compatibility
afhandelt — is waardevol voor de methodologie en voor toekomstige Olympus-migraties.

## Input

- Zeppelin's `test_dag_engine.py` die zowel v1- als v2-schemas test
- Git-history van de migratie-commits (wat werd toegevoegd, wat hernoemd, wat verwijderd)
- Eventuele migratie-notities die in de repo zelf staan

## Acceptatiecriteria

- [ ] Nieuw document `docs/schema-evolution.md` in Graaf Zeppelin met:
  - Waarom v2 nodig was (welke beperkingen had v1?)
  - Wat concreet veranderde (veld-voor-veld-diff)
  - Hoe migratie werd uitgevoerd (eenmalig script? forward-only of met rollback?)
  - Hoe backward-compat werd gehandhaafd (of bewust losgelaten)
  - Lessen: wat zou je nu anders doen?
- [ ] Cross-reference in Olympus' `docs/graph-methodology.md` §3 (lean JSON + content): "Zie Graaf Zeppelin voor een uitgewerkt migratievoorbeeld"
- [ ] Optioneel: een abstract migratie-patroon in een future § van de methodologie

## Aanpak

1. Spit de git-log door voor v2-gerelateerde commits
2. Interview-jezelf: waarom deed je het zo?
3. Schrijf het doc; houd het boven 2 en onder 5 kantjes

## Afhankelijkheden

Geen technische; vereist wel mentale ruimte voor reflectie. Kan parallel met alle
andere stories in deze epic.

## Geschat

2–3 uur.

## Risico's

- Geheugenverlies: details uit de migratie kunnen al lastig te reconstrueren zijn.
  Mitigatie: doe het nu, niet over drie maanden.
