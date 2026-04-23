# S14-07: Schema-evolutie documenteren als methodologie-bijdrage (GZ-07)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Laag
**Bron:** `docs/actieplan-os.md` §GZ-07

## Resultaat

- **`docs/schema-evolution.md`** aangemaakt (~290 regels, 6 secties):
  1. *Waarom v2 nodig was* — zes concrete beperkingen van v1 (geen
     domeinstructuur, geen edge-types, geen sliders, geen curve-
     functies, geen bronverwijzing, geen metadata).
  2. *Wat concreet veranderde* — top-level-tabel v1→v2, veld-voor-veld
     voor nodes (4→11) en edges (5→19, later 18 na S14-03),
     en de nieuwe sliders-top-level. Eindsom: ~190 → ~2 970 datapunten.
  3. *Hoe de migratie werd uitgevoerd* — code-based coexistence via
     `CausalDAG.from_dict`-autodetectie; v1-file blijft staan als
     museum-exemplaar; geen one-shot conversion-script.
  4. *Backward compat* — behouden op code-laag, losgelaten op
     product-laag; tests bewaken beide paden.
  5. *Schema-evolutie gaat door* — EPIC-14 tweaks (S14-01..S14-05)
     gedisciplineerd v2 verder zonder de versie-letter op te hogen.
  6. *Lessen* — zes reflecties: schema-versie expliciet meegeven,
     afgeleide velden niet in data, leegstring vs null, moderator-
     edges trade-off, migratiescript-wel-of-niet, coexistence als
     cheap insurance.
- **Cross-reference-sectie** beschrijft de voorgestelde haak in
  Olympus' `docs/graph-methodology.md` §3. De Olympus-kant is bewust
  buiten scope gelaten: dat is een kleine cross-repo-PR in de
  Olympus-conversatie, niet een wijziging aan Zeppelin.

## Niet gedaan (bewust)

- Geen wijzigingen aan Codebase-Olympus. De MCP-scope van deze sessie
  is `maxonamission/graaf_zeppelin` alleen; de cross-reference-patch
  aan Olympus wordt los opgepakt.
- Geen migratiehandleiding voor andere projecten. De lessen zijn
  observaties uit Zeppelin-praktijk, niet een prescriptief kader.

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
