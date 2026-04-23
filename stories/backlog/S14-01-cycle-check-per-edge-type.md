# S14-01: Cycle-check per edge-type (GZ-01)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Hoog
**Bron:** `docs/actieplan-os.md` §GZ-01

## Doel

De globale DAG-check in `app/core/dag_engine.py` vervangen door een
per-edge-type-check, zodat FEEDBACK-edges eindelijk feedback kunnen zijn en de
inconsistentie tussen schema en code opgeheven is.

## Context

`CausalDAG.__init__` (of `from_dict`) roept `nx.is_directed_acyclic_graph(self.graph)`
aan over de hele graph. Het JSON-schema kent vijf edge-types; alleen STRUCTURAL,
MEDIATING en MODERATOR moeten semantisch unidirectioneel zijn. SOCIAL_REGULATORY en
FEEDBACK zijn van nature cyclisch.

## Acceptatiecriteria

- [ ] Constante `ACYCLIC_EDGE_TYPES: frozenset[str] = frozenset({"STRUCTURAL", "MEDIATING", "MODERATOR"})` op module-level van `dag_engine.py`
- [ ] Helper `_acyclic_subgraph(graph) -> nx.DiGraph` die alleen edges met die types includeert
- [ ] `check_dag`-pad in `__init__` gebruikt de subgraph-variant: `nx.is_directed_acyclic_graph(_acyclic_subgraph(self.graph))`
- [ ] Bij falen: foutmelding noemt de edge(s) die de cyclus vormen én hun `edge_type`
- [ ] Nieuwe test `test_feedback_edges_may_form_cycles`: twee FEEDBACK-edges A↔B worden geaccepteerd
- [ ] Nieuwe test `test_structural_cycle_still_blocked`: STRUCTURAL A→B en STRUCTURAL B→A levert `ValueError`
- [ ] Bestaande `test_cycle_detection` blijft groen (mag expliciet STRUCTURAL gebruiken)
- [ ] README-snippet: één alinea over "welke edge-types mogen cyclisch zijn en waarom"

## Aanpak

1. Identificeer alle call-sites van de huidige acycliciteits-check (waarschijnlijk `__init__` + eventueel `add_relation`)
2. Voer `ACYCLIC_EDGE_TYPES` + helper in
3. Vervang de check; laat foutmeldingen de edge-types benoemen
4. Voeg de twee nieuwe tests toe
5. Aparte scope-beperkte PR; laag-risico refactor

## Afhankelijkheden

Geen. Kan als eerste story opgepakt worden.

## Geschat

4–6 uur inclusief tests en documentatie-snippet.

## Risico's

- `simulate_intervention` zou kunnen vastlopen op FEEDBACK-cycli als het recursief
  propageert zonder cap. Check of de bestaande `visited`-set of een max-depth de
  recursie afbreekt; zo niet, voeg dat toe als kleine veiligheid binnen deze story.
- Als de huidige dataset ergens FEEDBACK als globale-cyclus-bug bevat: die wordt
  zichtbaar zodra de strikte check weggaat. Dat is het punt — meld het transparant.
