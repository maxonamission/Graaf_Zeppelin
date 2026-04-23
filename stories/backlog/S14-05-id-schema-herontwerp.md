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

## Beslissing

**Direct integraal migreren, geen externe consumenten.** Alle `N###`/`E###`-IDs
worden in één ronde omgezet naar het hiërarchisch leesbare schema. Geen
mapping-compatibiliteitslaag nodig (er zijn nog geen rapporten/exports in omloop
die oude IDs bevatten). "Goed controleren" is expliciet onderdeel van de
acceptatiecriteria: per-node review van de mapping + audit-artefact.

Niet gekoppeld aan een toekomstige v3-schema-release — de migratie gaat los.

### Nog te bevestigen bij story-kickoff

- **Taal in ID-segmenten.** Default: **NL** voor `{DOMEIN}-{CATEGORIE}-{NIVEAU}`
  (bv. `SPORT-UIT-L0-001` met `UIT` = UITkomsten), consistent met de
  product-taal en bestaande `domain`/`level`-waardes. Edge-afkortingen volgen
  de bestaande EN `edge_type`-enum: `STR`, `MED`, `MOD`, `FBK`, `SREG`. Max te
  bevestigen voordat de validator wordt geschreven.
- **Categorie-afkortingen-tabel.** Eerst op papier vastleggen (bv. UIT, GED, REG,
  INF, ...) vóór migratiescript draait, anders drift tussen run en documentatie.

## Input

- Huidige 69 nodes en 108 edges in `sportdeelname_graph.json`
- Bestaande `domain`, `level`, `edge_type`-waardes als bron voor segmenten

## Acceptatiecriteria

- [ ] ID-patroon vastgelegd in `docs/id-schema.md` met voorbeelden én de categorie-afkortingen-tabel
- [ ] `validate_node_id(id: str) -> bool` en `parse_node_id(id: str) -> ParsedId` in `app/core/id_schema.py`
- [ ] Zelfde voor edges: `validate_edge_id`, `parse_edge_id`
- [ ] Pydantic-`Node` en `Edge` krijgen `@field_validator` die de ID tegen het schema checkt
- [ ] Migratiescript `scripts/migrate_ids.py` dat:
  - per bestaande node een nieuw ID afleidt uit `domain` + `level` + volgnr (+ categorie-mapping)
  - alle `source`/`target`-referenties in edges bijwerkt
  - een mapping-file `data/migrations/old_to_new_ids.json` achterlaat voor audit
  - idempotent is (tweede run = geen wijzigingen)
- [ ] **Review-stap**: mapping-file door Max gereviewd op alle 69 knopen (niet alleen steekproef) vóór commit van de gemigreerde JSON; afwijkingen gelogd met motivatie
- [ ] **Consistentiecheck**: na migratie draait S14-04's `validate_graph` groen (geen duplicate IDs, geen dangling refs, geen orphans nieuw ontstaan)
- [ ] Tests: validator accepteert geldige IDs en wijst ongeldige af met heldere boodschappen
- [ ] Migratiescript gedraaid; alle tests + cycle-check + validation blijven groen
- [ ] Oude `N###`/`E###`-refs in documentatie (`docs/`, `README.md`, `PLAN.md`, story-files) automatisch vervangen via mapping-file; handmatige sanity-check op één document

## Aanpak

1. Ontwerp schema op papier + categorie-afkortingen-tabel; laat Max bevestigen
2. Schrijf validator + parser (~50 regels)
3. Migratiescript met idempotentie en mapping-export
4. Droog-draai op kopie van JSON; review mapping-file **per knoop** (69 stuks, overzichtelijk)
5. Draai migratie op echte data; commit JSON + mapping-file samen
6. Vervang refs in repo-docs via mapping-file
7. Draai validation + testsuite

## Afhankelijkheden

- **S14-02** (Pydantic-validator hangt eraan)
- **S14-04** (`validate_graph` gebruikt als consistentie-check na migratie)

## Geschat

1 dag code + halve dag review van de mapping-file (volledige dekking i.p.v. steekproef).

## Risico's

- ID-collision bij latere uitbreiding met nieuwe domeinen. Mitigatie: reserveer
  `VOLGNR` ≥ 100 voor later toegevoegde items binnen een
  `{DOMEIN}-{CATEGORIE}-{NIVEAU}`-bucket.
- Categorie-afkortingen blijken bij review te grofmazig of dubbelzinnig →
  terug naar stap 1. Mitigatie: lijst eerst valideren tegen alle 69 bestaande
  node-labels voordat code geschreven wordt.
- Externe consumenten duiken alsnog op. Niet verwacht (bevestigd door Max), maar
  mitigatie is triviaal: mapping-file staat in `data/migrations/` en kan op verzoek
  gedeeld worden.
