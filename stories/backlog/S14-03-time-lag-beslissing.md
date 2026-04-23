# S14-03: Beslissing en implementatie rond `time_lag` (GZ-03)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-03

## Doel

Opheffen van het dead-field anti-pattern: `time_lag` wordt opgeslagen op elke edge
maar nergens gebruikt. Kies een pad en voer het door.

## Context

De appendix van de graph-methodologie noemt dit als één van de drie valkuilen voor
dynamische graph-projecten. Schemavelden die niet in gedrag landen, misleiden
reviewers, toekomstige zelf en LLM-gestuurde tools die "dit veld doet iets" aannemen.

## Beleidskeuze vooraf (Pad A of Pad B)

Eerst vastleggen welk pad gevolgd wordt — zie `docs/actieplan-os.md`
§"Open beleidskeuzes" vraag 1. Tussenvorm **Pad B nu + Pad A later** met expliciete
roadmap-regel is toegestaan.

### Pad A — activeer `time_lag` in simulatie (aanbevolen voor sportdeelname-domein)

- `simulate_intervention` iteratief over tijd; elke iteratie is één "tik"
- `time_lag: short` → effect na 1 tik; `medium` → 3 tikken; `long` → 10 tikken (parametriseer)
- Exporteer niet alleen eindtoestand maar traject: `[(t=0, values), (t=1, values), ..., (t=N, values)]`
- Frontend krijgt een tijdslider
- Effort: **3–5 dagen**

### Pad B — schrap `time_lag` uit het schema tot het werkt doet

- Verwijder het veld uit alle edges in de JSON (migratiescript)
- Schrap de validator (zodra S14-02 actief is)
- Zet in backlog als "later toevoegen als we interventie-dynamiek over tijd willen"
- Documenteer waarom het er nu niet is
- Effort: **half uur werk + review**

## Input

- Huidige edge-values voor `time_lag`: short / medium / long (categorisch)
- `simulate_intervention` in `dag_engine.py` met `propagate()`-subfunctie
- Overweging: worden beleidssimulaties al gebruikt in klantgesprekken of alleen intern?

## Acceptatiecriteria — Pad A

- [ ] Mapping `TIME_LAG_TICKS = {"short": 1, "medium": 3, "long": 10}` op module-level, aanpasbaar
- [ ] `simulate_intervention(factor, value, steps: int = 20)` produceert lijst van `(tick, node_values_dict)`
- [ ] Propagatie respecteert `time_lag`: effect van `long`-edge pas vanaf tick 10
- [ ] Frontend heeft tijdslider (of minimaal: return-payload bevat het hele traject)
- [ ] Tests: interventie op een keten met gemengde lags geeft verwachte stap-voor-stap uitkomst
- [ ] README vlagt expliciet wat één "tik" representeert (seizoen, jaar, ...)

## Acceptatiecriteria — Pad B

- [ ] Migratiescript `scripts/strip_time_lag.py` dat het veld uit de JSON verwijdert
- [ ] `time_lag` weg uit Pydantic-Edge-model (indien S14-02 live)
- [ ] README-alinea: "`time_lag` is verwijderd uit v2.X omdat de simulatie het niet gebruikt; toevoeging wacht op een aparte dynamiek-epic"
- [ ] Tests blijven groen

## Aanpak

- Kies pad
- Pad A: eerst prototyping op minimale fixture (3 nodes, gemengde lags) vóór op de echte 108-edge-dataset
- Pad B: 30-minuten klus

## Afhankelijkheden

Geen hard; praktisch wil je S14-02 (Pydantic) eerst, anders is de validator-wijziging
rommeliger.

## Geschat

3–5 dagen (A) of 30 minuten (B).

## Risico's

- **Pad A:** tik-dynamiek is lastig correct te krijgen bij FEEDBACK-cycli. Een
  positieve feedback-lus zonder demping → oneindige groei. Mitigeer met
  per-node-saturatie (zie `slider_engine.py`-curves) of max-delta-per-tik.
- **Pad A:** output-volume groeit (trajectenlijst × nodes × interventies); frontend
  moet dat aankunnen.
- **Pad B:** kans dat je later spijt krijgt en migratie terug moet doen. Laag risico:
  de data-structuur herstellen is triviaal als je de literatuur al hebt.
