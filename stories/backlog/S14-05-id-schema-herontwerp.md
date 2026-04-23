# S14-05: ID-schema herontwerpen (GZ-05)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-05

## Doel

Vervang opake IDs (`N001`, `E001`) door een hiërarchisch leesbaar schema. Maakt
diffs, discussies en exports begrijpelijk zonder naar de datatabel te hoeven kijken.

## Context

De rijke node-metadata (`domain`, `level`, `disciplines`) staat nu los van de ID. In
een leesbaar ID hoort die informatie in de ID zelf te zitten, als primaire ordening.

## Voorbeeld-schema (voorstel, te bediscussiëren)

```
Nodes:  {DOMEIN}-{CATEGORIE}-{NIVEAU}-{VOLGNR}
        SPORT-UIT-L0-001   (domein: Sport, categorie: UITkomsten, niveau: L0, volgnr: 001)
        SPORT-REG-L2-012   (domein: Sport, categorie: REGels & administratie, niveau: L2, volgnr: 012)

Edges:  E-{EDGE_TYPE_AFK}-{VOLGNR}
        E-MED-014          (MEDIATING, volgnr 014)
        E-FBK-007          (FEEDBACK, volgnr 007)
```

Alternatief, meer Olympus-achtig (eerst domein, dan type): `SPORT-UIT-ADULTSP-001`
(meer expressief, langer).

## Beleidskeuze

Zie `docs/actieplan-os.md` §"Open beleidskeuzes" vraag 2 — migreren of niet, en of
de v2→v3-ID's samen met een volgende schema-versie kunnen uitrollen.

## Input

- Huidige 69 nodes en 108 edges in `sportdeelname_graph.json`
- Bestaande `domain`, `level`, `edge_type`-waardes als bron voor segmenten

## Acceptatiecriteria

- [ ] ID-patroon vastgelegd in `docs/id-schema.md` met voorbeelden
- [ ] `validate_node_id(id: str) -> bool` en `parse_node_id(id: str) -> ParsedId` in `app/core/id_schema.py`
- [ ] Zelfde voor edges: `validate_edge_id`, `parse_edge_id`
- [ ] Pydantic-Node en Edge krijgen `@field_validator` die de ID tegen het schema checkt
- [ ] Migratiescript `scripts/migrate_ids.py` dat:
  - per bestaande node een nieuw ID afleidt uit `domain` + `level` + volgnr
  - alle `source`/`target`-referenties in edges bijwerkt
  - een mapping-file `old_to_new_ids.json` achterlaat voor audit
  - idempotent is (tweede run = geen wijzigingen)
- [ ] Tests: validator accepteert geldige IDs en wijst ongeldige af met heldere boodschappen
- [ ] Migratiescript gedraaid; alle tests + cycle-check + validation blijven groen

## Aanpak

1. Ontwerp het schema op papier — beleidsgevoelige keuze (welk domein-vocabulaire in de ID, NL of EN?)
2. Schrijf validator + parser (~50 regels)
3. Migratiescript
4. Draai migratie; review mapping-file op 5–10 steekproef-knopen
5. Publiceer mapping-file indien oude IDs in externe documentatie voorkomen

## Afhankelijkheden

S14-02 (Pydantic-validator hangt eraan).

## Geschat

1 dag code + halve dag discussie over schema-keuze.

## Risico's

- Externe documenten / presentaties met `N001`-refs zijn ineens "verouderd".
  Beleidskeuze: mapping-file voor toekomstige consultaties, of voorwaartse breuk.
- ID-collision bij latere uitbreiding met nieuwe domeinen. Mitigatie: reserveer
  `VOLGNR` ≥ 100 voor later toegevoegde items binnen een
  `{DOMEIN}-{CATEGORIE}-{NIVEAU}`-bucket.
