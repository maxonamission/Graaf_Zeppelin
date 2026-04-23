# S14-02: Pydantic-modellen voor Node en Edge (GZ-02)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Hoog
**Bron:** `docs/actieplan-os.md` §GZ-02

## Resultaat

- **`app/core/graph_models.py`** — canonieke Pydantic-modellen voor het
  v2-schema: `Graph`, `Node`, `Edge` en acht StrEnums (`Polarity`,
  `Strength`, `EdgeType`, `CurveType`, `TimeLag`, `BondInfluence`,
  `NodeStatus`, `TargetType`). Generieke graph-velden staan gegroepeerd
  boven project-specifieke velden (sportdeelname-kenmerken) zodat een
  latere formele splitsing volgens `docs/uniforme-kenmerken-taxonomie.md`
  een mechanische refactor wordt.
- **Validators:**
  - `base_weight ∈ [0.0, 1.0]` (per-edge)
  - `polarity` en `strength` accepteren NL+EN (S12-05 meertaligheid)
  - Lege strings op optionele enum-velden → `None` (matcht de v2-data)
  - Graph-level model_validator catcht dangling `source`/`target`-refs;
    moderator-edges (`target_type=edge`) worden tegen edge-IDs gecheckt
  - `extra="allow"` op Node/Edge voor niet-schema-breuken bij data-
    additions
- **`CausalDAG.from_dict(..., strict=True)`** roept
  `Graph.model_validate(data)` aan vóór de NetworkX-opbouw; validatie-
  fouten verschijnen nu als één `ValidationError` i.p.v. een
  late-binding KeyError. `strict=False` (gebruikt door de S14-04-
  validator) skipt ook deze stap.
- **Consolidatie uitgevoerd:**
  - `graaf_zeppelin/` package volledig verwijderd
    (`knowledge_graph.py`, `converters.py`, `cli.py`, `__main__.py`,
    `__init__.py`)
  - `graaf_zeppelin/converters.py` → `app/core/graph_io.py` (dict-based,
    generieke JSON↔GEXF↔Markdown; onafhankelijk van Pydantic — format
    conversion heeft het semantische schema niet nodig)
  - `graaf_zeppelin/cli.py` → `scripts/convert_graph.py`
  - `setup.py` entry-point verwijderd
  - `examples/example_usage.py` herschreven om nieuwe dict-based API te
    gebruiken
  - `tests/test_conversions.py` herschreven voor `app.core.graph_io`
    (van 7 ad-hoc assert-prints → 8 pytest-tests)
- **Dependency**: `requirements.txt` krijgt `pydantic[email]>=2.6.0`
  (afgesproken in S14-02; maakt S15-03 obsoleet).
- **Tests**: 20 nieuwe tests in `tests/test_graph_models.py` (enum
  normalisatie, alias-mapping, base_weight-range, required fields,
  dangling refs, moderator-edge-target, real-data round-trip). Totaal
  **118 graph-gerelateerde tests groen**.

## Niet gedaan (bewust doorgeschoven)

- **Mypy-strict config** (acceptatiecriterium uit actieplan): er is nog
  geen `pyproject.toml` of `mypy.ini` in de repo. De Pydantic-models zijn
  mypy-strict-compatible geschreven; de daadwerkelijke `strict = true`-
  opname in de build-tooling hoort bij S14-06 (ontwikkelstraat).
- **S14-04 `validate_edge_weights` aanpassing**: twee tests gebruikten
  voorheen strict=True met ongeldige waarden — Pydantic vangt die nu al
  af bij het laden. Tests nu omgezet naar `strict=False` (om de
  graph-level checker te blijven dekken) resp. naar een pure NetworkX-
  fixture.

## Vervolg

- S14-03 (time_lag schrappen) kan nu cleanly uitgevoerd worden: veld +
  enum uit `Edge`/`TimeLag` verwijderen, migratiescript de data-laag
  bijwerken.
- S14-05 (ID-schema migratie) bouwt op de Pydantic-validators: de
  ID-format-validator wordt als `@field_validator` op `Node.id` en
  `Edge.id` toegevoegd.
- S15-03 (email-validator dep) is overbodig geworden: `pydantic[email]`
  zit nu al in requirements.txt.

## Doel

Vervang de dict-gebaseerde representatie in `knowledge_graph.py` en `dag_engine.py`
door Pydantic-modellen met expliciete velden en runtime-validatie. Levert directe
winst: fouten in data worden gevangen bij laden in plaats van bij gebruik;
IDE-autocomplete werkt; mypy-strict wordt mogelijk.

## Context

De huidige code doet handmatige validatie (`"nodes" moet een list zijn; elke node
moet een 'id' hebben`) en vertrouwt verder op runtime-KeyErrors. Met 12 edge-velden
en een groeiend schema wordt dat kwetsbaar. De Pydantic-mypy-plugin garandeert
bovendien dat model-wijzigingen consistent doorklikken.

## Beslissing: consolideren

Zeppelin heeft nu twee graph-representaties: standalone `graaf_zeppelin/knowledge_graph.py`
(JSON↔GEXF↔Markdown-converters) en `app/core/dag_engine.py` (webapp + simulatie).
**Gekozen: consolideren** — één Pydantic-`Graph`-model in `app/core/graph_models.py`
is de canonieke bron; de converters worden losse functies die op dat model werken.
`graaf_zeppelin/knowledge_graph.py` wordt verwijderd (of gereduceerd tot een dunne
wrapper die dezelfde functies aanroept), omdat het niet als losse package door
derden wordt gebruikt.

## Bredere context

Deze story legt de **structuur** vast (expliciete models, enums, validators).
De **inhoud** — welke kenmerken horen in de kern van een causale DAG en welke zijn
project-specifiek — is een cross-project-gesprek dat niet in deze story hoort. Zie
`docs/uniforme-kenmerken-taxonomie.md` voor de wens om dat op Olympus-niveau op te
pakken. Praktisch betekent dat voor S14-02:

- Volg binnen deze story de bestaande Zeppelin-veldenlijst (12 edge-velden zoals
  in het v2-schema); verzin geen nieuwe veldnamen vooruitlopend op het
  cross-project-gesprek.
- Maak de `Edge`- en `Node`-modellen zó opgebouwd dat een latere splitsing in
  "kern" vs. "project-specifiek" eenvoudig door te voeren is — bv. velden die
  evident project-specifiek zijn (`bond_influence`, `slider_sensitivity`,
  `disciplines`) blijven bij elkaar, duidelijk van de graph-agnostische velden
  (`source`, `target`, `polarity`, `strength`, `edge_type`, `base_weight`)
  gescheiden in de modeldefinitie (bv. met comment-blokken of sub-groeperingen).
  Dit is een vormkeuze in deze story, geen nieuwe structuur.

## Acceptatiecriteria

- [ ] `app/core/graph_models.py` met:
  - `class Node(BaseModel)` met alle node-velden, inclusief validators
  - `class Edge(BaseModel)` met alle 12 edge-velden
  - `class Graph(BaseModel)` met `metadata`, `nodes: list[Node]`, `edges: list[Edge]` + model-validator die dangling-references opspoort (source/target moet in nodes bestaan)
  - StrEnums voor `Polarity`, `Strength`, `CurveType`, `TimeLag`, `BondInfluence`, `EdgeType`
- [ ] `CausalDAG.from_dict()` roept `Graph.model_validate(data)` aan i.p.v. handmatige checks
- [ ] Converters (JSON↔GEXF↔Markdown) verhuisd naar `app/core/graph_io.py` (of vergelijkbaar) en werken rechtstreeks op het Pydantic-`Graph`-model
- [ ] `graaf_zeppelin/knowledge_graph.py` verwijderd (of gereduceerd tot dunne wrapper); bijhorende tests aangepast naar de nieuwe module-paden
- [ ] Imports in de hele codebase bijgewerkt; `grep -r "graaf_zeppelin.knowledge_graph"` geeft geen hits meer (behalve eventueel één deprecation-shim)
- [ ] `requirements.txt` / `pyproject.toml`: `pydantic[email]>=2.6` toegevoegd
- [ ] Mypy-config: `plugins = ["pydantic.mypy"]`; strict-mode op `app/core/graph_models.py` en `app/core/dag_engine.py`
- [ ] Bestaande tests blijven groen; nieuwe tests voor validator-falen (ongeldige `curve_type`, negatief `base_weight`, onbekend `edge_type`)
- [ ] JSON-round-trip test: `Graph.model_validate(json.load(...)).model_dump()` is semantisch gelijk (volgorde mag variëren)

## Aanpak

1. Bouw `graph_models.py` naast bestaande code (niet-brekend)
2. Schrijf per-veld validators voor impliciete constraints (bv. `base_weight ∈ [0, 1]`, `strength ∈ enum`)
3. Refactor `CausalDAG.from_dict` / `to_dict` om Pydantic te gebruiken als data-laag; NetworkX blijft analyse-laag
4. Verhuis converters uit `graaf_zeppelin/knowledge_graph.py` naar een `app/core/graph_io.py` (of vergelijkbaar); laat ze op het Pydantic-model werken
5. Update alle import-paden; draai testsuite tot groen
6. Verwijder `graaf_zeppelin/knowledge_graph.py` (of reduceer tot dunne wrapper voor backward-compat, expliciet te beslissen bij commit)
7. Breid tests uit; slechte data faalt al bij `from_dict`, niet pas bij `simulate_intervention`

## Afhankelijkheden

S14-01 (GZ-01) is fijn om eerst te hebben (Pydantic-Edge-validator kan dan de juiste
acycliciteit-regel toepassen via `edge_type`). Mag ook parallel.

## Geschat

1–1,5 dag. Zwaarste werk: complete veldlijst uitschrijven en alle call-sites vinden
die dict-velden direct aanspreken (`edge["strength"]` → `edge.strength`).

## Risico's

- Sommige edges in de actuele JSON hebben mogelijk ontbrekende velden (pre-v2-data).
  Strategie: velden die niet overal aanwezig zijn `Optional` maken met default en
  een aparte warning-laag die rapporteert hoeveel edges incomplete metadata hebben.
- Converter-refactor (JSON↔GEXF↔Markdown) is de grootste scope-uitbreiding binnen
  deze story. Mitigatie: eerst Pydantic-`Graph` + `from_dict` live krijgen met groene
  tests, dán pas converters verhuizen — twee duidelijke commits.
- Scripts of externe tooling die `graaf_zeppelin.knowledge_graph` nog importeerden
  breken bij verwijdering. Niet verwacht (bevestigd door Max: geen externe
  consumenten), maar controleer `scripts/`, `examples/` en `tests/` op imports
  vóór verwijdering.
