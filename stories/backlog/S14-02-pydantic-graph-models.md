# S14-02: Pydantic-modellen voor Node en Edge (GZ-02)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Hoog
**Bron:** `docs/actieplan-os.md` §GZ-02

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
