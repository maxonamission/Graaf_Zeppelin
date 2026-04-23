# Actieplan voor Graaf Zeppelin

## Over dit document

Dit is een **extern actieplan** voor de repo `maxonamission/Graaf_Zeppelin`, geschreven vanuit Codebase-Olympus als staging-area. Het is bedoeld om in z'n geheel of in delen overgenomen te worden naar de Graaf-Zeppelin-repo (bv. als `docs/actieplan-os.md` of opgesplitst in `stories/`).

**Bron van de aanbevelingen:** de gedeelde [graph-methodologie](../graph-methodology.md) (acht conventies + appendix tijdsdimensie) zoals opgesteld bij Olympus, plus een verkenning van de huidige Graaf-Zeppelin-codebase op 20 april 2026.

**Lezer:** Max als ontwikkelaar van Graaf Zeppelin. De acties zijn solo-haalbaar, geen aannames over een team.

---

## Status-quo (april 2026)

### Wat Graaf Zeppelin nu is

- **Stack:** Python 3.x, FastAPI backend, Jinja2 + HTMX + D3 frontend ("intentioneel simpel voor beleidsambtenaren"), SQLite
- **Domein:** sportdeelname-beleid; 69 factoren, 108 relaties; 8 beleidssliders
- **Modules van belang:**
  - `graaf_zeppelin/knowledge_graph.py` — standalone package: dict-based `KnowledgeGraph`-klasse met `to_dict`/`from_dict`/`to_json`/`from_json` en converters naar GEXF / Markdown
  - `app/core/dag_engine.py` — webapp-gerichte `CausalDAG`-klasse: NetworkX, cycle-check, iteratieve propagatie via `simulate_intervention()`
  - `app/core/slider_engine.py` — modulefuncties voor curve-toepassing (DAMPENING_THRESHOLD, INVERTED_U_MOD, LINEAR_MOD), één-staps-evaluatie
  - `data/models/sportdeelname_graph.json` — v2-schema met rijke node- en edge-velden
- **Tests:** 15 testbestanden, expliciete `test_cycle_detection` + `test_simulate_intervention` voor de DAG-engine

### Wat het schema belooft

Elke edge in v2 heeft 12 velden:

| Veld | Voorbeeld-waardes |
|---|---|
| `id` | E001, E014, E059 |
| `source` / `target` | N001, N018 |
| `source_label` / `target_label` | menselijk leesbaar |
| `polarity` | positief / negatief / moderator |
| `strength` | sterk / midden / zwak |
| `curve_type` | LINEAR / THRESHOLD_LOGISTIC / INVERTED_U |
| `base_weight` | 0.0–1.0 |
| `time_lag` | short / medium / long |
| `bond_influence` | high / medium / low / none |
| `edge_type` | STRUCTURAL / MEDIATING / SOCIAL_REGULATORY / FEEDBACK / MODERATOR |
| `literature` | bronvermelding |
| `status` | A / B / - (validatieniveau) |
| `slider_sensitivity` | beleidshefboom-gevoeligheid |

### Wat de code doet

- `dag_engine.py` voert `nx.is_directed_acyclic_graph(self.graph)` uit op de **hele graph**: alle edge-types worden gelijk behandeld
- `simulate_intervention()` propageert iteratief, maar negeert `time_lag` volledig
- `slider_engine.py` past curve-functies toe in **één stap**, geen tijdsiteratie
- Geen Pydantic; alles dicts
- Geen orphan- of duplicate-detectie
- IDs zijn opaak: `N001`, `E001`

### De twee structurele inconsistenties

1. **Schema belooft FEEDBACK-edge-type, code weigert cycli.** Het edge-schema benoemt `edge_type=FEEDBACK` als legitiem, maar de globale acycliciteits-check accepteert geen enkele cyclus. Resultaat: FEEDBACK-edges kunnen niet bestaan in de praktijk; het schema-veld is misleidend.
2. **Schema belooft `time_lag`, simulatie negeert het.** `time_lag` wordt opgeslagen op elke edge maar nergens uitgelezen tijdens propagatie. Resultaat: dynamische effecten over tijd (sportdeelname-investering U8 die over jaren U14 raakt) komen niet uit de simulatie.

Beide zijn ontwerpschuld, geen bugs. De data-modellering loopt voor op de executable code.

---

## Score tegen de acht conventies + appendix

Met de bevindingen hierboven, gewogen op de genuanceerde lens uit de methodologie (per-edge-type-invarianten, appendix tijdsdimensie):

| # | Conventie | Score | Kerncommentaar |
|---|---|---|---|
| 1 | Pydantic-typen | ❌ | Dicts in `knowledge_graph.py` en `dag_engine.py`. Refactor zou onmiddellijke validatiewinst geven gezien de rijke 12-veld-edge-schemas. |
| 2 | ID-schema als contract | ❌ | `N001`, `E001` zijn opaak terwijl velden als `domain` en `level` rijke segmentering toelaten. `SPORT-UIT-L0-001` zou de positie meteen tonen. |
| 3 | Lean JSON + content separation | ⚠️ | Definities zitten in-JSON; `literature`-refs naar externe bronnen is een vorm van separation. Voor 69 nodes nog werkbaar; bij groei → splitsen. |
| 4 | Directory-mode loader | ❌ | Eén bestand. Niet urgent bij huidige omvang; moeilijk bij doorgroei naar bv. multi-discipline of multi-regio. |
| 5 | Invarianten-catalogus (per edge-type!) | ⚠️ | Cycle-check bestaat (anders dan ik aanvankelijk dacht), maar is **globaal** terwijl het schema FEEDBACK kent. Orphan en duplicate ontbreken. |
| 6 | Naamgevingsconventies | ⚠️ | `data/models/`, `app/core/` werkbaar, deels afwijkend van de methodologie-namen. Geen `validate_graph.py`-script met die exacte naam. |
| 7 | Layout- en visualisatie-defaults | ⚠️ | D3 in frontend, geen expliciete documentatie van layout-keuze. Voor een (deels-cyclisch) causaal netwerk past force-directed of circulair beter dan Sugiyama. |
| 8 | Test-patronen | ⚠️ | `test_cycle_detection`, `test_simulate_intervention`, v1/v2-schema-tests aanwezig; round-trip + invariant-based op de echte dataset ontbreken expliciet. |
| App. | Tijdsdimensie als first-class | ❌ | Dead-field anti-pattern op `time_lag`. Schema modelleert vertraging; simulatie behandelt alles instantaan. |

**Patroon:** alles wat met **structuur** te maken heeft, scoort goed-tot-redelijk. Alles wat met **dynamiek** of **schaal** te maken heeft, mist. Dat is consistent met een product dat "werkt voor de eerste use case" en nog niet door een tweede generatie eisen heen is gegaan.

---

## Mini-epic: zeven stories

### GZ-01: Cycle-check per edge-type

**Doel.** De globale DAG-check in `app/core/dag_engine.py` vervangen door een per-edge-type-check, zodat FEEDBACK-edges eindelijk feedback kunnen zijn en de inconsistentie tussen schema en code opgeheven is.

**Context.** `CausalDAG.__init__` (of de `from_dict`-classmethod) roept `nx.is_directed_acyclic_graph(self.graph)` aan over de hele graph. Het JSON-schema kent vijf edge-types; alleen STRUCTURAL, MEDIATING en MODERATOR moeten semantisch unidirectioneel zijn. SOCIAL_REGULATORY en FEEDBACK zijn van nature cyclisch.

**Input.**
- Huidige `dag_engine.py` met de globale check
- Edge-type-waardes uit `data/models/sportdeelname_graph.json`
- De Olympus-referentie: `src/gymnasium_classica/graph/validation.py` doet dit al goed met een hardcoded helper die transfer-edges filtert

**Acceptatiecriteria.**
- [ ] Constante `ACYCLIC_EDGE_TYPES: frozenset[str] = frozenset({"STRUCTURAL", "MEDIATING", "MODERATOR"})` op module-level van `dag_engine.py`
- [ ] Helper `_acyclic_subgraph(graph) -> nx.DiGraph` die alleen edges met die types includeert
- [ ] `check_dag`-pad in de `__init__` gebruikt de subgraph-variant: `nx.is_directed_acyclic_graph(_acyclic_subgraph(self.graph))`
- [ ] Bij falen: foutmelding noemt welke edge(s) de cyclus vormen én welk `edge_type` ze hebben — dat maakt debuggen sneller
- [ ] Nieuwe test `test_feedback_edges_may_form_cycles` met een minimale fixture: twee FEEDBACK-edges A↔B → graph wordt geaccepteerd
- [ ] Nieuwe test `test_structural_cycle_still_blocked` met STRUCTURAL A→B en STRUCTURAL B→A → `ValueError`
- [ ] Bestaande test `test_cycle_detection` blijft groen (mag eventueel aangepast worden om expliciet STRUCTURAL te gebruiken)
- [ ] README-snippet in de repo: één alinea over "welke edge-types mogen cyclisch zijn en waarom"

**Aanpak.**
1. Identificeer alle call-sites van de huidige acycliciteits-check (wrsch. alleen `__init__` + optioneel `add_relation`)
2. Voer `ACYCLIC_EDGE_TYPES` + helper in
3. Vervang de check; laat foutmeldingen de edge-types benoemen
4. Voeg twee tests toe
5. Commit als aparte scope-beperkte PR; dit is een laag-risico refactor

**Afhankelijkheden.** Geen. Kan als eerste story opgepakt worden.

**Geschat.** 4-6 uur inclusief tests en documentatie-snippet.

**Risico's.**
- `simulate_intervention` zou kunnen vastlopen op cycli in FEEDBACK-edges als het recursief propageert zonder cap. Check of de bestaande `visited`-set of een max-depth de recursie afbreekt; zo niet, voeg dat toe als kleine veiligheid binnen deze story.
- Als de huidige dataset ergens FEEDBACK als globale-cyclus-bug bevat: die wordt zichtbaar zodra je de strikte check weghaalt. Niet erg — dat is het punt — maar meld het transparant.

---

### GZ-02: Pydantic-modellen voor Node en Edge

**Doel.** Vervang de dict-gebaseerde representatie in `knowledge_graph.py` en `dag_engine.py` door Pydantic-modellen met expliciete velden en runtime-validatie. Levert onmiddellijke winst: fouten in data worden gevangen bij laden in plaats van bij gebruik; IDE-autocomplete werkt; mypy-strict wordt mogelijk.

**Context.** De huidige code doet handmatige validatie (`"nodes" moet een list zijn; elke node moet een 'id' hebben`) en vertrouwt verder op runtime-KeyErrors. Met 12 edge-velden en een groeiend schema wordt dat kwetsbaar. De Pydantic-mypy-plugin geeft je daarbovenop garantie dat je model-wijzigingen consistent doorklikken.

**Input.**
- Bestaande veldlijst uit `sportdeelname_graph.json` (zie tabel hierboven)
- Huidige `knowledge_graph.py` als refactor-target
- Enums die al impliciet bestaan: edge-types, curve-types, polarity, strength, time_lag, bond_influence

**Acceptatiecriteria.**
- [ ] `app/core/graph_models.py` (of vergelijkbare module) met:
  - `class Node(BaseModel)` met alle node-velden, inclusief validators
  - `class Edge(BaseModel)` met alle 12 edge-velden
  - `class Graph(BaseModel)` met `metadata`, `nodes: list[Node]`, `edges: list[Edge]` en een model-validator die dangling-references opspoort (source/target moet bestaan in nodes)
  - StrEnums voor `Polarity`, `Strength`, `CurveType`, `TimeLag`, `BondInfluence`, `EdgeType`
- [ ] `CausalDAG.from_dict()` roept `Graph.model_validate(data)` aan in plaats van handmatige checks
- [ ] `KnowledgeGraph` (standalone package) krijgt dezelfde refactor, of wordt gemarkeerd als deprecated met wijzing naar `app/core/graph_models.py` als canonieke bron
- [ ] `pyproject.toml` / `requirements.txt`: `pydantic[email]>=2.6` toegevoegd
- [ ] Mypy-config (ook als nieuwe stap): `plugins = ["pydantic.mypy"]`; strict-mode op `app/core/graph_models.py` en `app/core/dag_engine.py`
- [ ] Alle bestaande tests blijven groen; nieuwe tests voor validator-falen (ongeldige curve_type, negatief base_weight, onbekend edge_type)
- [ ] JSON-round-trip test: `Graph.model_validate(json.load(...)).model_dump()` produceert semantisch gelijke data (volgorde mag variëren)

**Aanpak.**
1. Bouw `graph_models.py` naast de bestaande code (niet-brekend)
2. Schrijf per-veld validators waar de huidige code impliciete constraints heeft (bv. `base_weight ∈ [0, 1]`, `strength ∈ enum`)
3. Refactor `CausalDAG.from_dict` / `to_dict` om Pydantic als de data-laag te gebruiken, NetworkX blijft de analyse-laag
4. Deprecate of refactor `KnowledgeGraph`; dit is een keuze (zie "Open vragen" verderop)
5. Breid tests uit; doel is dat slechte data nu al faalt bij `from_dict`, niet pas bij `simulate_intervention`

**Afhankelijkheden.** GZ-01 is fijn om eerst te hebben (dan kun je de Pydantic-Edge-validator de juiste acycliciteit-regel toepassen via de edge-type). Maar kan ook parallel.

**Geschat.** 1-1,5 dag. Het zwaarste is de complete veldlijst uitschrijven en alle call-sites vinden die dict-velden direct aanspreken (`edge["strength"]` → `edge.strength`).

**Risico's.**
- Sommige edges in de actuele JSON hebben mogelijk ontbrekende velden (pre-v2-data die niet helemaal is bijgewerkt). Bij strikte validatie → failure on load. Strategie: maak velden die niet overal aanwezig zijn `Optional` met default, en voeg een aparte warning-laag toe die rapporteert hoeveel edges incomplete metadata hebben.
- De standalone `knowledge_graph.py` heeft converters (JSON ↔ GEXF ↔ Markdown). Die moeten mee-refactoren of expliciet achter een dict-API blijven werken. Beslissing valt binnen deze story.

---

### GZ-03: Beslissing en implementatie rond `time_lag`

**Doel.** Opheffen van het dead-field anti-pattern: `time_lag` wordt opgeslagen op elke edge maar nergens gebruikt. Kies een pad en voer het door.

**Context.** De appendix van de methodologie noemt dit als een van de drie valkuilen voor dynamische graph-projecten. Schemavelden die niet in gedrag landen, misleiden reviewers, toekomstige jezelf en LLM-gestuurde tools die "dit veld doet iets" aannemen.

**Twee paden — beleidskeuze vooraf:**

**Pad A: activeer `time_lag` in simulatie (aanbevolen voor sportdeelname-domein).**
- Maak `simulate_intervention` iteratief over tijd; elke iteratie is één "tik"
- `time_lag: short` → effect werkt in 1 tik door; `medium` → 3 tikken; `long` → 10 tikken (of andere mapping, parametriseer)
- Exporteer niet alleen eindtoestand maar trajectenlijst: `[(t=0, values), (t=1, values), ..., (t=N, values)]`
- Frontend krijgt een tijdslider om de traject-stap te kiezen
- Effort: **3-5 dagen**

**Pad B: schrap `time_lag` uit het schema tot je er iets mee gaat doen.**
- Verwijder het veld uit alle edges in de JSON (migratiescript)
- Schrap de validator (zodra GZ-02 actief is)
- Zet het in backlog als "later toevoegen als we interventie-dynamiek over tijd willen"
- Documenteer waarom het er nu niet is
- Effort: **half uur werk** + review

**Input.**
- Huidige edge-values voor `time_lag`: short / medium / long (categorisch, niet numeriek)
- `simulate_intervention` in `dag_engine.py` met zijn `propagate()`-subfunctie
- Overweging: worden beleidssimulaties al gebruikt in klantgesprekken of alleen intern getest?

**Acceptatiecriteria — Pad A.**
- [ ] Mapping `TIME_LAG_TICKS = {"short": 1, "medium": 3, "long": 10}` op module-level, aanpasbaar
- [ ] `simulate_intervention(factor, value, steps: int = 20)` produceert een lijst van `(tick, node_values_dict)`
- [ ] Propagatie respecteert `time_lag`: effect van edge A→B met `long` is pas zichtbaar vanaf tick 10, niet tick 1
- [ ] Frontend heeft een tijdslider (of minimaal: return-payload bevat het hele traject)
- [ ] Tests: interventie op een keten met gemengde lags geeft verwachte stap-voor-stap uitkomst
- [ ] Documenteer dat tikken "seizoenen" representeren (of wat dan ook je kiest) — vlag expliciet in README

**Acceptatiecriteria — Pad B.**
- [ ] Migratiescript `scripts/strip_time_lag.py` dat het veld uit de JSON verwijdert
- [ ] `time_lag` weg uit Pydantic-Edge-model (indien GZ-02 live)
- [ ] README-alinea: "`time_lag` is verwijderd uit v2.X omdat de simulatie het niet gebruikt; toevoeging wacht op een aparte dynamiek-epic"
- [ ] Tests blijven groen

**Aanpak.**
- Kies pad (zie "Open vragen" verderop)
- Voor A: eerst prototyping op minimale fixture (3 nodes, gemengde lags) vóór op de echte 108-edge-dataset
- Voor B: 30-minuten klus

**Afhankelijkheden.** Geen hard; praktisch wil je GZ-02 (Pydantic) eerst, anders is de validator-wijziging rommeliger.

**Geschat.** 3-5 dagen (A) of 30 min (B).

**Risico's.**
- Pad A: stip-dynamiek is lastig correct te krijgen bij FEEDBACK-cycli. Een positieve feedback-lus zonder demping → oneindige groei. Mitigeer met per-node-saturatie (zie `slider_engine.py`-curves) of max-delta-per-tik.
- Pad A: output-volume groeit (trajectenlijst × nodes × interventies); frontend moet dat aankunnen.
- Pad B: kans dat je later spijt krijgt en migratie terug moet doen. Laag risico: de data-structuur herstellen is triviaal als je de literatuur al hebt.

---

### GZ-04: Invarianten-catalogus aanvullen

**Doel.** Cycle-check (na GZ-01), orphan-detectie, duplicate-ID-detectie, dangling-edge-references en edge-value-validaties als één `validation.py` met `ValidationReport`-output; draaien in CI.

**Context.** Olympus' `graph/validation.py` is hiervoor model — zowel de `ValidationReport`-dataclass als de losse check-functies (`detect_cycles`, `find_orphan_nodes`, `check_connectivity`, `validate_edge_weights`, `validate_node_ids`) zijn grotendeels overneembaar.

**Input.**
- Olympus-`validation.py` als referentie (niet kopiëren-en-aanpassen; schrijven met de Zeppelin-specifieke edge-schema in gedachten)
- Pydantic-modellen uit GZ-02 (validatie-per-edge wordt deels gratis via Pydantic; deze story gaat over **graph-niveau** invarianten)

**Acceptatiecriteria.**
- [ ] `app/core/validation.py` met `ValidationReport`-dataclass (is_valid, node_count, edge_count, cycles, orphan_nodes, weakly_connected_components, warnings, errors)
- [ ] Functies:
  - `detect_cycles(graph, *, acyclic_edge_types)` — gebruikt GZ-01's helper
  - `find_orphan_nodes(graph)` — nodes zonder edges
  - `find_duplicate_ids(raw_data)` — vóór NetworkX-opbouw, op de raw JSON
  - `check_connectivity(graph)` — components
  - `validate_edge_weights(graph)` — `base_weight ∈ [0,1]`, `strength ∈ enum`
- [ ] `validate_graph(graph) -> ValidationReport` als orchestrator
- [ ] Script `scripts/validate_graph.py` — CLI die de JSON laadt, report draait, exit-code !=0 bij errors
- [ ] CI-step (zie GZ-06) roept dit aan
- [ ] Tests: één per check-functie met fixture die faalt en één die slaagt
- [ ] ValidationReport wordt optioneel geprint door `simulate_intervention` bij `--verbose` of in logs

**Aanpak.**
1. Kopieer de structuur van Olympus' `validation.py` conceptueel; herschrijf met Zeppelin's edge-velden
2. `find_duplicate_ids` draait op de rauwe JSON-data vóór NetworkX (omdat NetworkX stilzwijgend dedupliceert bij `add_node`)
3. Maak `validate_graph.py` CLI met `argparse`
4. Vroege integratie in de loader (`CausalDAG.from_dict()` roept `validate_graph` aan en raised bij errors); ook mogelijk als aparte aanroep

**Afhankelijkheden.** GZ-01 (voor correcte cycle-detection). Profiteert van GZ-02 maar niet strikt.

**Geschat.** Halve dag tot een dag.

**Risico's.** Performance op grotere datasets: Olympus draait valideren op 800 knopen binnen milliseconden. Voor 69 knopen triviaal.

---

### GZ-05: ID-schema herontwerpen

**Doel.** Vervang opake IDs (`N001`, `E001`) door hiërarchisch leesbaar schema. Maakt diffs, discussies en exports begrijpelijk zonder naar de datatabel te hoeven kijken.

**Context.** De rijke node-metadata (`domain`, `level`, `disciplines`) staat nu los van de ID. In een leesbaar ID hoort die informatie in de ID zelf te zitten, als primaire ordening.

**Voorbeeld-schema (voorstel, te bediscussiëren).**
```
Nodes:  {DOMEIN}-{CATEGORIE}-{NIVEAU}-{VOLGNR}
        SPORT-UIT-L0-001   (domein: Sport, categorie: UITkomsten, niveau: L0, volgnr: 001)
        SPORT-REG-L2-012   (domein: Sport, categorie: REGels & administratie, niveau: L2, volgnr: 012)

Edges:  E-{EDGE_TYPE_AFK}-{VOLGNR}
        E-MED-014          (MEDIATING, volgnr 014)
        E-FBK-007          (FEEDBACK, volgnr 007)
```

Alternatief, meer Olympus-achtig (eerst domein, dan type):
```
SPORT-UIT-ADULTSP-001      (meer expressief, langer)
```

**Input.**
- Huidige 69 nodes en 108 edges in `sportdeelname_graph.json`
- De bestaande `domain`, `level`, `edge_type`-waardes als bron voor de segmenten

**Acceptatiecriteria.**
- [ ] ID-patroon vastgelegd in `docs/id-schema.md` met voorbeelden
- [ ] `validate_node_id(id: str) -> bool` en `parse_node_id(id: str) -> ParsedId` in `app/core/id_schema.py`
- [ ] Zelfde voor edges: `validate_edge_id`, `parse_edge_id`
- [ ] Pydantic-Node en Edge krijgen een `@field_validator` die de ID tegen het schema checkt
- [ ] Migratiescript `scripts/migrate_ids.py` dat:
  - per bestaande node een nieuw ID afleidt uit `domain` + `level` + volgnr
  - alle `source`/`target`-referenties in edges bijwerkt
  - een mapping-file `old_to_new_ids.json` achterlaat voor audit
  - idempotent is (tweede run = geen wijzigingen)
- [ ] Tests: validator accepteert geldige IDs en wijst ongeldige af met heldere boodschappen
- [ ] Migratiescript draaien; alle tests blijven groen; cycle-check + validation blijven groen

**Aanpak.**
1. Ontwerp het schema op papier met Max — beleidsgevoelige keuze (welk domein-vocabulaire in de ID, Engels of Nederlands?)
2. Schrijf validator + parser (~50 regels code)
3. Migratiescript
4. Draai migratie; review de mapping-file op 5-10 steekproef-knopen
5. Als iemand oude IDs in externe documentatie heeft staan: maak de mapping-file publiek beschikbaar

**Afhankelijkheden.** GZ-02 (Pydantic-validator hangt eraan).

**Geschat.** 1 dag code + halve dag discussie over schema-keuze.

**Risico's.**
- Externe documenten / presentaties die `N001`-refs bevatten zijn ineens "verouderd". Beleidskeuze: mapping-file voor toekomstige consultaties, of voorwaartse breuk.
- ID-collision als je later verder uitbreidt met nieuwe domeinen. Mitigatie: reserveer `VOLGNR` ≥ 100 voor later toegevoegde items binnen een `{DOMEIN}-{CATEGORIE}-{NIVEAU}`-bucket.

---

### GZ-06: Ontwikkelstraat parallel aan Olympus

**Doel.** Pas de volledige ontwikkelstraat (zoals gebouwd in de OS-epic van Olympus) toe op Graaf Zeppelin: lint + types + pre-commit + CI + Claude-hooks + review-skills + story-workflow + CLAUDE.md-sectie.

**Context.** Graaf Zeppelin heeft al pytest en een behoorlijk brede testsuite, maar mist pre-commit, CI-workflow (of heeft minimaal), Claude Code hooks, story-conventie, PR-template. Door het hele patroon in één epic door te voeren wordt Zeppelin even goed beschermd als Olympus. Wordt aanzienlijk lichter zodra er een template-repo is.

**Input.**
- De acht OS-stories van Olympus (OS-01 t/m OS-08) als blauwdruk
- Olympus' `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`, `.claude/settings.json` + hooks, `scripts/check_story_status.py` + `migrate_legacy_done_stories.py`, PR-template, CLAUDE.md-sectie

**Acceptatiecriteria.**
- [ ] `pyproject.toml` (of `requirements.txt`-equivalent) heeft `ruff`, `mypy`, `pre-commit` in dev-deps
- [ ] `[tool.ruff]` + `[tool.ruff.lint]` + `[tool.ruff.format]` geconfigureerd; rules-set identiek aan Olympus minus Griekse-unicode-uitzondering (die is Olympus-specifiek)
- [ ] `[tool.mypy]` met `strict = true` op `app/core/` (minimaal), pydantic-plugin actief
- [ ] `.pre-commit-config.yaml` met ruff-check, ruff-format, mypy (local hook), EOF/whitespace/yaml-toml-json-check, secret-scanner, story-status-check
- [ ] `.github/workflows/ci.yml` met ruff + mypy + pytest + story-status op elke PR + push
- [ ] `.claude/settings.json` met PostToolUse (ruff-op-py) + Stop (pytest)
- [ ] `.github/pull_request_template.md` (kopie van Olympus, aangepast voor Zeppelin-security-triggers: auth/licensing/LLM-connector/externe API's)
- [ ] `stories/`-structuur met `backlog/`, `doing/`, `done/` + `EPICS.md`; bestaande stories migreren als die er al zijn, of de epics uit dit document als eerste entries opzetten
- [ ] `scripts/check_story_status.py` — kopie uit Olympus, aangepast zodat paden kloppen
- [ ] `CLAUDE.md` met `## Ontwikkelstraat`- en `## Story-workflow`-secties
- [ ] Branch protection op `main` activeren zodra CI stabiel draait

**Aanpak.**
Splits in sub-stories, analoog aan Olympus' OS-01 t/m OS-08, in dezelfde volgorde:

1. GZ-06a: Ruff strict config + auto-fix ronde
2. GZ-06b: Mypy strict op `app/core/`
3. GZ-06c: Pre-commit hooks
4. GZ-06d: CI-workflow (GitHub Actions)
5. GZ-06e: Claude Code hooks
6. GZ-06f: Story-status-check en story-conventie
7. GZ-06g: Review-skills in PR-workflow
8. GZ-06h: CLAUDE.md-sectie

Draai incrementeel; commit na elke sub-story; houd de testsuite groen. Exact het model uit Olympus.

**Afhankelijkheden.**
- Voor maximale winst: doe GZ-01 t/m GZ-05 eerst, zodat de ontwikkelstraat daarna een stabiele codebase bewaakt. Maar het kan ook parallel: laag 1 (ruff/mypy) levert onmiddellijk feedback op refactors.
- **Speciaal:** als er intussen een template-repo `codebase-templates` bestaat (zie aparte discussie), krijgt GZ-06 een heel ander karakter: niet acht sub-stories, maar één keer `copier copy` en hooguit een paar project-specifieke tweaks.

**Geschat.**
- Zonder template: 1 werkweek verspreid (zoals Olympus' OS-epic)
- Met template: halve dag

**Risico's.**
- De bestaande 15 testbestanden gaan mogelijk ruff-issues opleveren (zoals Olympus ook had met 117 errors bij default-rules). Niet-functionele wijzigingen; pak het in één commit met ruff-auto-fix.
- Mypy-strict op `app/core/` ontdekt wrsch. dict-signaturen die pas door GZ-02 wel strict worden. Workaround: activeer mypy-strict alleen op de Pydantic-module als eerste; op `dag_engine.py` pas na GZ-02.

---

### GZ-07: Schema-evolutie documenteren als methodologie-bijdrage

**Doel.** De v1→v2-schemamigratie die Zeppelin al heeft doorgemaakt expliciet documenteren als voorbeeld voor andere graph-projecten. Bijdrage aan de gedeelde methodologie.

**Context.** Olympus heeft (nog) geen schema-migratie achter de rug; Zeppelin wel. De kennis hoe je dat doet — welke stappen, welke valkuilen, hoe je backward-compatibility afhandelt — is waardevol voor de methodologie en voor toekomstige Olympus-migraties.

**Input.**
- Zeppelin's `test_dag_engine.py` die zowel v1- als v2-schemas test
- Git-history van de migratie-commits (wat werd toegevoegd, wat hernoemd, wat verwijderd)
- Eventuele migratie-notities die in de repo zelf staan

**Acceptatiecriteria.**
- [ ] Nieuw document `docs/schema-evolution.md` in Graaf Zeppelin met:
  - Waarom v2 nodig was (welke beperkingen had v1?)
  - Wat concreet veranderde (veld-voor-veld-diff)
  - Hoe migratie werd uitgevoerd (eenmalig script? forward-only of met rollback?)
  - Hoe backward-compat werd gehandhaafd (of bewust losgelaten)
  - Lessen: wat zou je nu anders doen?
- [ ] Cross-reference in Olympus' `docs/graph-methodology.md` §3 (lean JSON + content): "Zie Graaf Zeppelin voor een uitgewerkt migratievoorbeeld"
- [ ] Optioneel: een abstract migratie-patroon in een future § van de methodologie

**Aanpak.**
1. Spit de git-log door voor v2-gerelateerde commits
2. Interview-jezelf: waarom deed je het zo?
3. Schrijf het doc; houd het boven 2 en onder 5 kantjes

**Afhankelijkheden.** Geen technische; vereist wel mentale ruimte voor reflectie.

**Geschat.** 2-3 uur.

**Risico's.**
- Geheugenverlies: details uit de migratie kunnen al lastig te reconstrueren zijn. Mitigatie: doe het nu, niet over drie maanden.

---

## Open beleidskeuzes

Drie vragen die vóór de eerste story beantwoord moeten worden:

**1. `time_lag` — Pad A of Pad B?** (Zie GZ-03 voor details.) De vraag is in essentie: hoe centraal zijn dynamische, temporele interventie-vragen voor het product? Als beleidsgebruikers zeggen "ik wil zien hoe investering in U8 over zes jaar doorwerkt in seniorsdeelname", is Pad A noodzakelijk en urgent. Als ze zeggen "ik wil zien welke factoren samenhangen", is Pad B verdedigbaar en scheelt weken werk.

Tussenvorm: **Pad B nu + Pad A later** met expliciete roadmap-regel. Voorkomt dat het veld "vaag aanwezig" is.

**2. ID-schema — wel of niet migreren?** (Zie GZ-05.) Semantisch grote winst, maar raakt alle externe documentatie. Twee sub-vragen:
- Zijn er al externe consumenten van de IDs (rapporten, presentaties, exports naar beleidsambtenaren)?
- Kun je de v2-ID's tegelijk met een volgende schema-versie (v3?) uitrollen? Dan wordt het één breuk in plaats van twee.

**3. `knowledge_graph.py` (standalone) — behouden of consolideren met `dag_engine.py`?** Er zijn nu twee graph-representaties in Zeppelin: de standalone `KnowledgeGraph` (voor format-conversies: JSON↔GEXF↔Markdown) en `CausalDAG` (voor webapp + simulatie). Bij GZ-02 moet je kiezen:
- **Consolideren:** één Pydantic-`Graph`-model; de converters worden losse functies die op het Pydantic-model werken
- **Behouden:** `KnowledgeGraph` blijft een export-laag, `CausalDAG` is de analyse-laag; beide parse dezelfde JSON via Pydantic

Aanbeveling: **consolideren**, tenzij `knowledge_graph.py` als losse package door derden gebruikt wordt (dan breek je iemand anders' code).

---

## Aanbevolen volgorde en afhankelijkheden

```
GZ-01 (cycle-check per type)        —→ levert correcte invariant voor GZ-04
  ↓
GZ-02 (Pydantic-refactor)           —→ validatie-fundering voor GZ-04 + GZ-05
  ↓
GZ-04 (invarianten-catalogus)       —→ dekt data-kwaliteit vóór grote migraties
  ↓
GZ-03 (time_lag-beslissing)         —→ kan parallel met GZ-05; maar na GZ-02
  ↓
GZ-05 (ID-schema migratie)          —→ raakt alle refs; doe dit als de rest stabiel is
  ↓
GZ-06 (ontwikkelstraat)             —→ eindfase: bewaking over al het voorgaande
  ↓
GZ-07 (schema-evolutie doc)         —→ kan op elk moment; laagste inspanning
```

**Parallellisatie.** GZ-07 kan de hele tijd parallel (alleen docs). GZ-01 en GZ-02 zijn afzonderlijk werk en kunnen parallel als je twee sessies hebt (zij het dat GZ-02 profiteert van GZ-01 in z'n tests).

**Kritisch pad:** GZ-01 → GZ-02 → GZ-04 → GZ-05. Geschat: 3-4 dagen kritisch werk, plus GZ-03 (A of B) en GZ-06 als eigen tracks.

**Totaal effort (Pad A voor time_lag):** ~2-3 werkweken
**Totaal effort (Pad B voor time_lag):** ~1,5 werkweek

---

## Expliciete niet-scope

Wat bewust **niet** in dit actieplan hoort, hoe graag we het ook zouden doen:

- **Schaalvergroting voorbereiden (10⁵+ knopen).** Zeppelin heeft 69 knopen; een graphdatabase-migratie is overkill en wordt pas relevant bij een orde-van-grootte sprong. §3 en §4 van de methodologie dekken dat dan.
- **Frontend-refactor.** Jinja2 + HTMX + D3 is bewust gekozen voor de doelgroep; geen reden om naar React te migreren. Dit plan raakt alleen de data- en analyselaag.
- **LLM-integratie doorlichten.** `llm_connector.py` en `llm_guard.py` bestaan al en verdienen een eigen security-review (inclusief `/security-review`-triggers zodra GZ-06 staat), maar vallen buiten de graph-methodologie.
- **Licensing / release-management aanpassen.** Dat is product-architectuur, niet graph-architectuur.
- **Unificatie met Olympus-codebase.** De projecten delen een methodologie, niet een codebase. Geen monorepo-experimenten.
- **Automatische PR-reviewer via Claude-API als GitHub-action.** Mooie idee, maar hoort in een eventuele `codebase-templates`-epic, niet hier.

---

## Tot slot

Het werk hier is ruim 2-3 weken focus-tijd. Dat kan in één blok of verspreid over twee maanden met rustigere weken tussendoor — afhankelijk van hoe snel je beleidssimulatie-functionaliteit wilt aanscherpen.

Een aanbeveling: **doe GZ-01 binnen een week na deze notitie.** Het is goedkoop, het repareert een concrete inconsistentie, en zolang het niet gebeurt werkt het model anders dan het schema belooft. Alle andere stories kunnen wachten tot een natuurlijk moment; GZ-01 verdient dat niet.

Vragen, pushback of aanpassingen? Bespreek in de Olympus-conversatie — dit document is een eerste draft vanuit externe blik, niet een vastgestelde route.
