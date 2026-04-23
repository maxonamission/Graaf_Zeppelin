# S14-05: ID-schema herontwerpen (GZ-05)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-05

## Resultaat

- **`app/core/id_schema.py`** — canonieke module met de 9-domein-tabel,
  5 edge-type-afkortingen, `L1/L2 → L12` niveau-normalisatie, plus
  `validate_node_id`, `validate_edge_id`, `parse_node_id`,
  `parse_edge_id`, `derive_node_id`, `derive_edge_id`. 47 tests in
  `tests/test_id_schema.py` borgen format, tabellen en edge-cases.
- **`scripts/migrate_ids.py`** — idempotent migratiescript.
  Per-bucket-sequencing: nodes binnen `(domain, level)`, edges binnen
  `edge_type`. Werkt alle ID-verwijzingen bij (`source`, `target`, én
  `slider.related_nodes`). Dry-run + expliciete `--indent` zodat de
  bestaande 3-spaties-stijl bewaard blijft.
- **Migratie uitgevoerd** op `data/models/sportdeelname_graph.json`:
  **69/69 node-IDs** en **114/114 edge-IDs** herschreven. Audit-mapping
  in `data/migrations/old_to_new_ids.json` (gecommit, klein bestand).
  Per-node review uitgevoerd (alle 69 regels met label + domein + level
  naast het nieuwe ID); alles plausibel. Tweede run idempotent: no-op.
- **Pydantic-validators** op `Node.id` (strict, altijd) en `Edge.id`
  (strict bij niet-lege string). Invalid formats raisen meteen een
  helpful `ValidationError` bij `Graph.model_validate`.
- **Docs**: nieuwe `docs/id-schema.md` met tabellen, voorbeelden en
  uitbreidingsprocedure. `docs/AUDIT.md` en `docs/epic_slider_qualifiers.md`
  bijgewerkt met nieuwe IDs via de mapping-file. Geen resterende
  ongeïdentificeerde `N###`/`E###`-refs in docs.
- **Tests**: alle 168 graph-gerelateerde tests groen (test_id_schema:
  47, test_dag_engine: 54, test_validation: 23, test_graph_models: 24,
  test_conversions: 8, test_slider_engine: 12). Fixtures uit
  test_dag_engine, test_graph_models, test_validation, test_api,
  test_integration en test_slider_engine gemigreerd naar Vorm A.
  `scripts/validate_graph.py` nog altijd `is_valid=True` op de
  gemigreerde data.

## Niet blokkerend, wel bekend

- **`test_api.py`** en **`test_integration.py`** hebben nog meer N-IDs
  in asserties die ik niet uitputtend heb nagelopen, omdat die
  testfiles momenteel niet eens worden gecollecteerd (EPIC-15 S15-01
  pytest-asyncio). De `N001` → `UIT-L0-001` vervangingen die ik kon
  vinden zijn wel doorgevoerd zodat ze niet direct stuk gaan zodra
  S15-01 rond is.

## Vervolg

Mapping-file blijft staan voor toekomstige cross-references (bv.
externe rapporten die alsnog oude IDs blijken te hebben, of een
cross-project-taxonomie-revisie — zie
`docs/uniforme-kenmerken-taxonomie.md`).

## Doel

Vervang opake IDs (`N001`, `E001`) door een hiërarchisch leesbaar schema. Maakt
diffs, discussies en exports begrijpelijk zonder naar de datatabel te hoeven kijken.

## Context

De rijke node-metadata (`domain`, `level`, `disciplines`) staat nu los van de ID. In
een leesbaar ID hoort die informatie in de ID zelf te zitten, als primaire ordening.

## Vastgelegd ID-schema (Vorm A)

**De data heeft geen `category`-veld** — 9 domeinen × 5 levels = 45 buckets voor
69 knopen, ruim voldoende. ID-vorm is dus `{DOMEIN-AFK}-{NIVEAU}-{VOLGNR}`, geen
categorie-segment, geen overkoepelend prefix (de hele graph is één onderwerp).

```
Nodes:  {DOMEIN-AFK}-{NIVEAU}-{VOLGNR}
        UIT-L0-001     (Uitkomsten, L0, volgnr 001)
        REG-L2-004     (Regels & Administratie, L2, volgnr 004)
        TRP-L1-012     (Training & Prestatie, L1, volgnr 012)

Edges:  E-{EDGE_TYPE_AFK}-{VOLGNR}
        E-MED-014      (MEDIATING, volgnr 014)
        E-FBK-007      (FEEDBACK, volgnr 007)
```

### Domein-afkortingen (bindend voor deze story)

| Domein                  | Afk.  |
|-------------------------|-------|
| Uitkomsten              | `UIT` |
| Regels & Administratie  | `REG` |
| Sociaal                 | `SOC` |
| Psychologisch           | `PSY` |
| Middelen & Logistiek    | `MDL` |
| Organisatie & Aanbod    | `ORG` |
| Training & Prestatie    | `TRP` |
| Macro-context           | `MAC` |
| Discipline-specifiek    | `DIS` |

Alle afkortingen zijn 3 letters (fixed-width, prettig sorteerbaar).

### Edge-afkortingen (uit bestaande EN `edge_type`-enum)

`STR` (STRUCTURAL), `MED` (MEDIATING), `MOD` (MODERATOR), `FBK` (FEEDBACK),
`SREG` (SOCIAL_REGULATORY). Edge-IDs blijven EN om spiegel te houden met de
enum die al in de code staat; node-IDs zijn NL omdat domein-namen NL zijn. Die
asymmetrie is verdedigbaar: edges zijn een technisch begrip, knopen zijn
domein-inhoud.

### Niveau-normalisatie

`L1/L2` wordt genormaliseerd naar `L12` in de ID (fixed-width segment). Andere
niveaus blijven `L0`, `L1`, `L2`, `L3`. Het oorspronkelijke `level`-veld op de
node blijft ongewijzigd (dus nog `L1/L2` in de JSON) — de ID is een *afgeleide*
weergave, geen vervanger van het veld zelf.

## Beslissing: direct integraal migreren

Geen externe consumenten, dus geen mapping-compatibiliteitslaag nodig. "Goed
controleren" is expliciet onderdeel van de acceptatiecriteria: per-node review
van de mapping + audit-artefact in `data/migrations/old_to_new_ids.json`. Niet
gekoppeld aan een toekomstige v3-schema-release — migratie gaat los.

## Bredere context

Dit ID-schema is het eerste concrete experiment met uniforme graph-object-
taxonomie. Zie `docs/uniforme-kenmerken-taxonomie.md` voor de wens om op
cross-project-niveau (Zeppelin + Olympus + toekomstige graph-projecten) te
werken aan een gedeelde set kenmerken voor nodes én edges. Als dat cross-project
gesprek leidt tot aanpassingen in de `domain`- of `edge_type`-taxonomie, moet
het ID-schema eventueel meebewegen. Daarom wordt de mapping-file bewaard.

## Input

- Huidige 69 nodes en 114 edges in `sportdeelname_graph.json`
- Bestaande `domain`, `level`, `edge_type`-waardes als bron voor segmenten

## Acceptatiecriteria

- [ ] `docs/id-schema.md` aangemaakt met het volledige schema (vorm, tabel, edge-afkortingen, L12-conventie) — gebruik het "Vastgelegd ID-schema"-blok hierboven als baseline
- [ ] `validate_node_id(id: str) -> bool` en `parse_node_id(id: str) -> ParsedId` in `app/core/id_schema.py`
- [ ] Zelfde voor edges: `validate_edge_id`, `parse_edge_id`
- [ ] Pydantic-`Node` en `Edge` krijgen `@field_validator` die de ID tegen het schema checkt
- [ ] Migratiescript `scripts/migrate_ids.py` dat:
  - per bestaande node een nieuw ID afleidt uit `domain` + `level` (→ afkortingen-tabel + L12-normalisatie) + volgnr
  - alle `source`/`target`-referenties in edges bijwerkt
  - edge-IDs afleidt uit `edge_type` + volgnr
  - een mapping-file `data/migrations/old_to_new_ids.json` achterlaat voor audit
  - idempotent is (tweede run = geen wijzigingen)
- [ ] **Review-stap**: mapping-file door Max gereviewd op alle 69 knopen (niet alleen steekproef) vóór commit van de gemigreerde JSON; afwijkingen gelogd met motivatie
- [ ] **Consistentiecheck**: na migratie draait S14-04's `validate_graph` groen (geen duplicate IDs, geen dangling refs, geen orphans nieuw ontstaan)
- [ ] Tests: validator accepteert geldige IDs en wijst ongeldige af met heldere boodschappen
- [ ] Migratiescript gedraaid; alle tests + cycle-check + validation blijven groen
- [ ] Oude `N###`/`E###`-refs in documentatie (`docs/`, `README.md`, `PLAN.md`, story-files) automatisch vervangen via mapping-file; handmatige sanity-check op één document

## Aanpak

1. `docs/id-schema.md` aanmaken met het vastgelegde schema als baseline
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

- ID-collision bij latere uitbreiding. Mitigatie: reserveer `VOLGNR` ≥ 100 voor
  later toegevoegde items binnen een `{DOMEIN-AFK}-{NIVEAU}`-bucket.
- De huidige afkortingen-tabel blijkt bij review te grofmazig of dubbelzinnig
  (bv. `REG` voor "Regels" verwarrend met generieke "regel"). Mitigatie: valideer
  de tabel tegen alle 69 bestaande node-labels **voordat** de code geschreven wordt.
  Bij serieuze twijfel: tabel herzien in overleg met Max, nooit eenzijdig.
- Cross-project-taxonomie-gesprek (zie `docs/uniforme-kenmerken-taxonomie.md`)
  leidt later tot andere `domain`-naamgeving → ID-schema moet meebewegen. Laag
  risico: mapping-file is er juist voor, en de tabel staat op één plek.
- Externe consumenten duiken alsnog op. Niet verwacht (bevestigd door Max),
  maar mitigatie is triviaal: mapping-file staat in `data/migrations/`.
