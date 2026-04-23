# S14-04: Invarianten-catalogus aanvullen (GZ-04)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Hoog
**Bron:** `docs/actieplan-os.md` §GZ-04

## Resultaat

- `app/core/validation.py` met `ValidationReport`-dataclass en
  zes invarianten-functies (`detect_cycles`, `find_orphan_nodes`,
  `find_duplicate_ids`, `find_dangling_refs`, `check_connectivity`,
  `validate_edge_weights`) plus de `validate_graph`-orchestrator.
  `detect_cycles` hergebruikt `_acyclic_subgraph` uit S14-01.
- `scripts/validate_graph.py` CLI met `--json` en `--fail-on-warnings`;
  exit-codes 0 (valid) / 1 (errors of warnings-bij-flag) / 2 (bad file).
- `CausalDAG.from_dict(..., strict=False)` toegevoegd zodat de validator
  alle invarianten in één rapport kan verzamelen i.p.v. te falen op de
  eerste cyclus; bestaande `strict=True` default is onveranderd.
- `tests/test_validation.py` met 21 tests: per invariant één
  passend-én-falend-fixture, plus een orchestrator-test op een gemengde
  dirty fixture en een smoke-test op de echte `sportdeelname_graph.json`.
- **Bevinding op echte data**: `sportdeelname_graph.json` is
  `is_valid=True`; wel één informatieve warning ("graph heeft 2
  weakly-connected components") omdat `N066` alleen via een
  moderator-edge (E099) aan de graaf hangt, niet via een gewone
  NetworkX-edge. Geen data-probleem — wel waardevol om expliciet te
  weten. De orphan-check sluit moderator-bronnen correct uit (anders
  was `N066` ten onrechte als orphan gerapporteerd).
- Alle 99 graph-gerelateerde tests (`test_dag_engine.py`,
  `test_validation.py`, `test_slider_engine.py`,
  `test_prompt_builder.py`, `test_conversions.py`) groen.

## Vervolg

De CI-aanroep van `scripts/validate_graph.py` valt onder S14-06
(ontwikkelstraat). `ValidationReport` kan in S14-05 gebruikt worden als
consistentiecheck ná de ID-migratie (al als afhankelijkheid vastgelegd
in S14-05).

## Doel

Cycle-check (na S14-01), orphan-detectie, duplicate-ID-detectie,
dangling-edge-references en edge-value-validaties als één `validation.py` met
`ValidationReport`-output; draaien in CI.

## Context

Olympus' `graph/validation.py` is model hiervoor — zowel de `ValidationReport`-
dataclass als de losse check-functies (`detect_cycles`, `find_orphan_nodes`,
`check_connectivity`, `validate_edge_weights`, `validate_node_ids`) zijn grotendeels
overneembaar, maar herschrijven met Zeppelin's edge-schema in gedachten (niet
klakkeloos kopiëren).

## Input

- Olympus-`validation.py` als referentie
- Pydantic-modellen uit S14-02 (validatie-per-edge wordt deels gratis via Pydantic;
  deze story gaat over **graph-niveau** invarianten)

## Acceptatiecriteria

- [ ] `app/core/validation.py` met `ValidationReport`-dataclass (is_valid, node_count, edge_count, cycles, orphan_nodes, weakly_connected_components, warnings, errors)
- [ ] Functies:
  - `detect_cycles(graph, *, acyclic_edge_types)` — gebruikt helper uit S14-01
  - `find_orphan_nodes(graph)` — nodes zonder edges
  - `find_duplicate_ids(raw_data)` — vóór NetworkX-opbouw, op raw JSON
  - `check_connectivity(graph)` — components
  - `validate_edge_weights(graph)` — `base_weight ∈ [0,1]`, `strength ∈ enum`
- [ ] `validate_graph(graph) -> ValidationReport` als orchestrator
- [ ] Script `scripts/validate_graph.py` — CLI die JSON laadt, report draait, exit-code !=0 bij errors
- [ ] CI-step (zie S14-06) roept dit aan
- [ ] Tests: per check-functie één fixture die faalt én één die slaagt
- [ ] `ValidationReport` wordt optioneel geprint door `simulate_intervention` bij `--verbose` of in logs

## Aanpak

1. Neem de structuur van Olympus' `validation.py` conceptueel over; herschrijf met Zeppelin's edge-velden
2. `find_duplicate_ids` draait op rauwe JSON-data vóór NetworkX (omdat NetworkX stilzwijgend dedupliceert bij `add_node`)
3. Maak `validate_graph.py` CLI met `argparse`
4. Vroege integratie in loader (`CausalDAG.from_dict()` roept `validate_graph` aan en raised bij errors); ook mogelijk als aparte aanroep

## Afhankelijkheden

S14-01 (voor correcte cycle-detection). Profiteert van S14-02 maar niet strikt.

## Geschat

Halve dag tot een dag.

## Risico's

Performance op grotere datasets: Olympus draait valideren op 800 knopen binnen
milliseconden. Voor 69 knopen triviaal.
