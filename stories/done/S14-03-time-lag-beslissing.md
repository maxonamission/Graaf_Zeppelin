# S14-03: `time_lag` schrappen (Pad B), Pad A op roadmap (GZ-03)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-03

## Resultaat

- **`scripts/strip_time_lag.py`** — idempotent migratiescript met
  `--dry-run` en `--indent`; draaien op `data/models/sportdeelname_graph.json`
  verwijderde het veld uit **114/114 edges**. Tweede run: no-op. JSON-
  indentatie (3 spaties) bewaard.
- **`TimeLag` StrEnum verwijderd** uit `app/core/graph_models.py`; korte
  comment op die plek die expliciet naar PLAN.md verwijst voor Pad A.
- **`time_lag` veld verwijderd** uit `Edge`-model en uit de validator-
  lijst. Docstring bij `_empty_to_none` bijgewerkt met ander voorbeeld.
- **Test fixtures**: `"time_lag": ""` uit de v2-fixture in
  `tests/test_dag_engine.py` (drie edges) gehaald. In
  `tests/test_graph_models.py`: `TimeLag`-import weg, enum-assertie
  weg, `test_empty_string_becomes_none` gebruikt nu `curve_type` en
  `edge_type` i.p.v. `time_lag`. Nieuwe regressietest
  `test_time_lag_removed` borgt dat noch de enum noch het veld
  terugkruipt.
- **`PLAN.md`**: nieuwe sectie "Toekomstige uitbreiding — dynamiek-epic
  (`time_lag`, Pad A)" onder Fase 4, met blueprint (tik-dynamiek,
  FEEDBACK-demping, frontend-tijdslider) en expliciete trigger.
- **`README.md`**: korte alinea "`time_lag` uit het schema (v2.X)" met
  verwijzing naar de roadmap-regel.
- **Tests**: 119 graph-gerelateerde tests groen.
- **Validator op echte data**: `scripts/validate_graph.py` rapporteert
  nog steeds `is_valid=True` (enige warning is de ongewijzigde
  weakly-connected-components bevinding van S14-04).

## Dataformat-impact

Het v2-schema kent nu 11 edge-velden in plaats van 12. Geen andere
wijzigingen aan data-structuren. De `slider_engine.py`-propagatie werkt
nog altijd in één stap — geen codewijzigingen daar nodig omdat de code
`time_lag` sowieso al negeerde.

## Beslissing

**Pad B nu, Pad A op roadmap.** `time_lag` wordt verwijderd uit schema en data; de
iteratieve-tikken-simulatie (Pad A) komt terug als aparte epic zodra er een concrete
product-aanleiding is (bv. klantvraag om trajecten over tijd).

Motivatie: zolang de simulatie het veld niet gebruikt, is de huidige situatie een
dead-field anti-pattern dat reviewers en LLM-tools misleidt. Pad B lost dat nu op
voor ~30 min werk; Pad A is later netter op te bouwen bovenop een stabiele
Pydantic-basis (S14-02) en een afgemaakte invarianten-catalogus (S14-04).

## Doel

Opheffen van het dead-field anti-pattern: `time_lag` uit JSON en schema halen, met
expliciete roadmap-regel die Pad A vastpint als toekomstige uitbreiding.

## Context

De appendix van de graph-methodologie noemt dit als één van de drie valkuilen voor
dynamische graph-projecten. Schemavelden die niet in gedrag landen, misleiden
reviewers, toekomstige zelf en LLM-gestuurde tools die "dit veld doet iets" aannemen.

## Input

- Huidige edge-values voor `time_lag`: short / medium / long (categorisch)
- `simulate_intervention` in `dag_engine.py` met `propagate()`-subfunctie
- Pydantic-Edge-model uit S14-02 (indien live op moment van uitvoering)

## Acceptatiecriteria

- [ ] Migratiescript `scripts/strip_time_lag.py` dat het veld uit de JSON verwijdert (idempotent)
- [ ] `time_lag` weg uit Pydantic-`Edge`-model (vereist S14-02 live) én uit `TimeLag` StrEnum
- [ ] Schema-documentatie in `docs/` geüpdatet (veld niet langer genoemd, of gemarkeerd als "gereserveerd voor toekomstige dynamiek-epic")
- [ ] README-alinea: "`time_lag` is verwijderd in v2.X omdat de simulatie het niet gebruikt; heractivatie wacht op de dynamiek-epic (zie roadmap)"
- [ ] Expliciete **roadmap-regel** in `PLAN.md` (of aparte `ROADMAP.md`) onder "Toekomstige uitbreiding": **Dynamiek-epic (heractiveren `time_lag`, Pad A)** — trigger: eerste concrete klantvraag naar trajecten-over-tijd
- [ ] Tests blijven groen; eventuele tests die `time_lag` inspecteerden worden verwijderd of omgebouwd

## Aanpak

1. Draai migratiescript op `data/models/sportdeelname_graph.json`; inspecteer diff
2. Verwijder veld + enum uit Pydantic-model
3. Zoek op `time_lag` in de hele codebase; verwijder resterende verwijzingen
4. Update README + roadmap-regel
5. Draai testsuite groen

## Afhankelijkheden

**S14-02 (Pydantic) moet live zijn** voor de model-wijziging schoon te doen. Zonder
S14-02 is het kaal-JSON-strippen nog steeds mogelijk, maar rommeliger.

## Geschat

30 minuten tot 1 uur (migratiescript + doc-wijzigingen + roadmap-regel + testrun).

## Risico's

- Kans dat Pad A later wél urgent wordt en we de data terug moeten migreren. Laag
  risico: de literatuur heeft de lag-waardes al, herstel is triviaal via de git-
  history van de JSON of een nieuwe derivatie-ronde.
- Zolang Pad A niet is uitgevoerd, mist de simulatie dynamiek. Bewust aanvaarde
  beperking — vlag duidelijk in README en in UI-copy rond simulatieresultaten.

## Roadmap-vervolg (Pad A, niet in deze story)

Eigen toekomstige epic/story zodra getriggerd. Blueprint voor dan:

- Mapping `TIME_LAG_TICKS = {"short": 1, "medium": 3, "long": 10}`, parametriseerbaar
- `simulate_intervention(factor, value, steps: int = 20)` produceert traject: `[(tick, node_values_dict), ...]`
- FEEDBACK-demping: per-node-saturatie (bestaande `slider_engine.py`-curves) of max-delta-per-tik, anders oneindige groei in positieve lussen
- Frontend-tijdslider; payload-volume groeit (trajectenlijst × nodes × interventies) — dimensioneren op bestaande dashboard-performance
- README documenteert wat één "tik" betekent (seizoen, jaar, ...)
