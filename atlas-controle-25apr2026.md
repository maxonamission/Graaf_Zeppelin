# Controle inrichting `codebase_atlas` — 25 april 2026

**Branch gecontroleerd:** `claude/import-action-plan-OSoWH` (laatste commit 2026-04-25)
**Vergeleken met:** vorige snapshot (zelfde branch, voor 24 mrt) en
verkenning-v2 §8 harmonisatie-voorstellen.
**Toegang:** WebFetch op publieke URLs (GitHub-MCP is restricted tot graaf_zeppelin).

---

## Sinds vorige check

**9 → 17 commits.** Mapstructuur ongewijzigd; protocol verfijnd
(v0.3 met `improves`/`shapes`/`erodes`); meta-architectuur aangevuld
(cross-level edges gekwantificeerd); geen werkvloer-laag toegevoegd
(geen CLAUDE.md, geen registers, geen CI).

Laatste vijf commits (24-25 apr): "§4.5 expliciteer kadert", "§4.5
normeert→kadert", "herstructureer werkconcept-positie",
"hygiëne na L3-sync en protocol-reframe", "synchroniseer L3-cijfers
naar v11.3 (51N · 176E)" — focus op documentatie en herstructurering.

---

## Samenvatting in één blik

| Categorie | Status | Belangrijkste observatie |
|---|---|---|
| A. Repo-werkvloer voor LLM | ⚠ | leeswijzer ✓, README ✓, CLAUDE.md ✗ |
| B. Story-hygiene en -tooling | ✗ | geen cross-model checker; per model wisselende tooling |
| C. Protocol-governance | ⚠ | protocol uitstekend; geen validator/governance-procedure |
| D. Cross-project registers | ✗ | geen van de 5 voorgestelde registers aanwezig |
| E. CI / kwaliteitsbewaking | ✗ | geen `.github/`, geen `.pre-commit`; .gitignore wel adequaat |
| F. Cross-level relaties | ✓ | 55/26/6 edges expliciet, niveau-autonomie vastgelegd |
| G. Verhouding tot Graaf Zeppelin | ✗ | geen verwijzing naar webapp-implementatie |
| H. Documentatie-coherentie | ⚠ | verwijzingen kloppen, datums divergeren over 4 maanden |
| I. Modelspecifieke gezondheid | ⚠ | L1 templates ✓, L3 templates ✗, stories-tellingen inconsistent |

**Eindconclusie:** protocol-laag (cat C) en cross-level-architectuur (cat F)
zijn sterk; werkvloer-laag (CLAUDE.md, registers, CI, governance-procedures)
is grotendeels nog open. Drie ROI-stappen onderaan.

---

## Categorie A — Repo-werkvloer voor LLM

**A1. CLAUDE.md op root: ✗ ontbreekt nog steeds.**
Direct GET op `raw.githubusercontent.com/.../CLAUDE.md` levert 404.
Grootste gat — elke nieuwe Claude-sessie moet uitvinden hoe de repo werkt.

**A2. `docs/leeswijzer.md`: ✓ aanwezig.**
Met origineel bewaard als `docs/leeswijzer-zip-origineel.md`. Aangepast
aan de root-structuur (atlas-root = wat in de zip `Modelbouw/` was).

**A3. Top-level `README.md`: ✓ consistent.**
Datum 2026-04-24. Beschrijft protocol, hiërarchie L1→L2→L3, naamgeving,
Kanban. Sluit aan op leeswijzer en verkenning. Geen inhoudelijke conflicten.

---

## Categorie B — Story-hygiene en tooling

**B1. Cross-model story-hygiene-checker: ✗ ontbreekt.**
`_scripts/` bevat alleen `migrate_frontmatter.py` en `rename_stories.py`.
Geen equivalent van Zeppelins `check_story_status.py`. Status-drift tussen
`EPICS_*.md` en `stories/<status>/` niet bewaakt.

**B2. Per model wisselende eigen tooling: ⚠ geen gedeelde standaard.**
- **L3** heeft uitgebreide validatoren: `validate_knowledge_graph.py`,
  `audit_cross_references.py`, `detect_register_duplicates.py`,
  `validate_literatuurregister.py`, `validate_model_literature.py`,
  `scenario_doorwandeling.py`, `scenario_impact_analyse.py`,
  `sync_monolithic_graph.py`, `link_edges_to_register.py`,
  `link_nodes_to_register.py`, `convert_knowledge_graph_v2.py`,
  `generate_bronnoverzicht.py`, `review_lit_assignments.py` — 13 stuks.
- **L2** heeft `AVV_match.py`, `AVV_score.py`, `AVV_validate.py`,
  `AVV_validate_questionnaire.py`, `avv_graph.py`,
  `generate_onepager_mermaid.py`, `mojibake_fix.py` — 7 stuks,
  domein-specifiek.
- **L1** heeft alleen `build_model.py`, `convert_md_to_json.py` — basaal.

Tooling-volwassenheid divergeert sterk. L3-patronen (validators) zijn
porteerbaar naar A_-niveau, maar dat is niet gebeurd.

**B3. Backlog/doing/done-structuur: ⚠ niet centraal geverifieerd.**
A_ heeft een `stories/`-submap; aannemelijk dat andere modellen
vergelijkbaar zijn. Zonder checker manueel werk om te toetsen.

---

## Categorie C — Protocol-governance (A_-laag)

**C1. `gedeeld_protocol.md`: ✓ uitstekend.**
Versie **0.3** (geëffectueerd 25 maart 2026). Bevat:
- **8 edge-types met polariteit en voorbeelden**: 5 core (`enables` +,
  `threatens` −, `requires` +, `modulates` ±, `competes_with` −) +
  3 extended (`improves` +, `shapes` +, `erodes` −).
- **4 curve-types met formules en parameters**:
  - `LINEAR`: `y = base_weight × polarity × x` (geen params).
  - `SATURATING`: `y = bw × pol × (1 − e^(−k × x))` (k > 0).
  - `THRESHOLD`: `y = bw × pol × σ(k × (x − t))` (t ∈ [0,1], k > 0).
    Let op: protocol gebruikt `THRESHOLD`, niet `THRESHOLD_LOGISTIC`.
  - `INVERTED_U`: `y = bw × pol × exp(−((x−μ)²/(2σ²)))` (μ, σ).
- **node_class** (regular/stock) ortogonaal aan **role** (capability/etc.).
  Stock vereist `change_rate` (slow=jaren / medium=maanden / fast=weken).
- **Evidence-schaal A/B/C** met expliciete criteria, plus
  **evidence-object** met `ref_id` (`REF_{Author}_{Year}`), `source`,
  `detail`, `type` (empirical/theoretic/expert/analogy).
- **Slider-schema**: `id`, `label`, `definition`, `type`
  (globaal/selectief), `curve_type`, `default`, `range`.
- **Cross-level principe** (§7.4): stock op N → slider op N-1.
- **Version history** compleet:
  - v0.1 (2026-02-20) — initial concept uit veldaudit.
  - v0.2 (2026-03-24) — `improves`/`shapes` toegevoegd; stock/capability
    subtypes (D2 → C1 herpositionering).
  - v0.3 (2026-03-25) — node_class/role split; `erodes` toegevoegd;
    cross-level stock→slider geformaliseerd.
- **ID-conventie**: `{PREFIX}{NR}` strings, niet-prescriptieve prefix per
  model.
- **Validatie regel 3**: geen orphan nodes.

**C2. Protocol-validator-script: ✗ niet zichtbaar.**
`A_.../scripts/` bevat `pipeline.py`, `run_realistic_case.py`,
`realistic_case_output.json` — geen `validate_protocol.py` die per JSON-
graaf afdwingt dat edge_types/curve_types/node_class binnen v0.3-vocabulaire
vallen. L3 heeft eigen `validate_knowledge_graph.py`, maar die is
domein-specifiek, geen protocol-conformiteit-check.

**C3. Governance-procedure voor protocol-changes: ✗ ontbreekt.**
Het protocol erkent dit zelf expliciet:
> "The protocol explicitly does not prescribe governance procedures."

Descriptief voor bestaande modellen (VM, AVV, NSkiV); prescriptief voor
nieuwe (mandatory fields). Geen review-board, geen change-procedure, geen
impact-assessment-stap. Verkenning §9-B1/B3 blijft open.

**C4. Pipeline operationeel: ✓ route D in werking.**
`A_/scripts/pipeline.py` + `run_realistic_case.py` +
`realistic_case_output.json` aanwezig. Deterministische micro→meso→macro
doorrekening werkt.

---

## Categorie D — Cross-project registers (verkenning §8.2)

Geen van de vijf voorgestelde registers is aanwezig.

**D1. Cross-model slider-register: ⚠ deels.**
`A_.../docs/E05_S03_slider_inventaris.md` is een 17-sliders-inventaris,
maar dat is een **statisch protocol-doc** voor de referentie-implementatie
GVM. Een *levend* cross-model register dat per slider aangeeft "in welke
modellen, met welke defaults, met welke afwijkingen" ontbreekt.

**D2. Stock-node-register per niveau: ✗ ontbreekt.**
De architectuurnotitie noemt stock-kandidaten in proza; een gedeelde lijst
(per L2/L3 een document met de erkende stocks en hun change_rate) ontbreekt
als zelfstandig artefact.

**D3. Domein-taxonomie-mapping: ✗ ontbreekt.**
Geen document dat D1's 9 domeinen ↔ GVM's 5 dimensies expliciet aan elkaar
koppelt.

**D4. Evidence-bibliografie gedeeld: ✗ ontbreekt.**
Per-model wel: L3 heeft `validate_literatuurregister.py` + `generate_
bronnoverzicht.py`. Een centrale `references.bib`-equivalent over alle
modellen heen ontbreekt.

**D5. Protocol-release-kalender: ✗ ontbreekt.**
Het protocol heeft een Appendix B (version history terugkijkend), maar geen
vooruitkijkende kalender "welke modellen op welke protocolversie staan en
wanneer ze upgraden".

---

## Categorie E — CI / kwaliteitsbewaking

**E1. `.github/workflows/`: ✗ map bestaat niet.**
Direct GET levert 404. Geen automatische validatie bij commits/PRs.

**E2. `.pre-commit-config.yaml`: ✗ bestaat niet.**
Direct GET levert 404. Geen pre-commit hooks.

**E3. `.gitignore`: ✓ adequaat.**
Inhoud: Python (`__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.venv/`,
`venv/`, `.ipynb_checkpoints/`), OS (`.DS_Store`, `Thumbs.db`), editors
(`.vscode/`, `.idea/`, `*.swp`, `*~`), overig (`.obsidian/`, `logs/`,
`cache/`, `*.log`). Goed afgesteld voor Python-projecten met Obsidian-
authoring.

**Consequentie:** wijzigingen in atlas worden niet automatisch gevalideerd.
Voor een meta-repo waar zes modellen samenkomen is dit een lacune die groeit
naarmate er meer cross-cutting werk plaatsvindt.

---

## Categorie F — Cross-level relaties geformaliseerd

**F1. `meta-architectuur.md` kwantificeert expliciet: ✓.**
- **L1↔L2 emergentie**: 55 cross-level edges.
- **L2→L3 upward**: 26 edges.
- **L3→L2 feedback**: 6 loops.
- Totaal L2↔L3: 32 edges.

Quote: *"55 cross-level edges verbinden L1-nodes met L2-nodes."* en
*"26 meso→macro edges + 6 macro→meso feedbackloops verbinden L2 en L3."*

**F2. "Niveau-autonomie is primaat": ✓ expliciet vastgelegd in §3.5.**
Quote: *"De relatie is alleen actief wanneer L2 en L3... gezamenlijk
worden ingezet; in een zelfstandige L2-toepassing ontbreekt dit kader."*
En: het toepassen van L3's framework op L2 is *"een ontwerpkeuze bij
concrete toepassing, niet een gegeven van het model."*

**F3. Cross-level stock→slider-principe: ✓ geformaliseerd in protocol v0.3 §7.4.**
Test: *"Is this value externally set as a scenario parameter, or does the
system generate it internally?"* Sluit aan bij verkenning §4 en de
architectuurnotitie.

**F4. Concrete invulling per model: ⚠ nog werk.**
Sliders zijn als "verticale doorwerkingsketens" beschreven; per-model
mapping (welke L3-stocks worden L2-sliders, welke L2-stocks worden L1-
sliders) is in de modellen zelf nog niet expliciet gemaakt (verkenning
§8.1).

---

## Categorie G — Verhouding tot Graaf Zeppelin (D1)

**G1. `D1_/PROJECTSTATUS_D1.md`: ✗ noemt geen runnable implementatie elders.**
Datum 22 februari 2026. Versie v2.3.0. 69 nodes / 114 edges / 9 domeinen
/ 8 sliders. Geen verwijzing naar "Graaf Zeppelin", "webapp" of synchronisatie-
procedure.

**G2. D1 JSON's behandeld als "single source of truth" in atlas.**
PROJECTSTATUS positioneert D1-bestanden in atlas als leidend; geen
afgeleide-status of mirror-vermelding.

**G3. Risico op stille divergentie: ⚠.**
Parallel werk in beide repo's (atlas D1-spec, Graaf Zeppelin D1-runnable)
zonder afspraak welke leidend is. Een korte verhoudingsverklaring in
`D1_/README_D1.md` of `PROJECTSTATUS_D1.md` zou dit voorkomen.

---

## Categorie H — Documentatie-coherentie

**H1. Verwijzingen tussen hoofdstukken: ✓ kloppen.**
README, leeswijzer, verkenning, meta-architectuur, protocol verwijzen
correct naar elkaar. Geen verweesde links geconstateerd in de
hoofdstroom.

**H2. Datum-divergentie: ⚠ vier verschillende datums.**
- README atlas: **2026-04-24**
- PROJECTSTATUS_Modelbouw: **2026-03-25**
- Protocol v0.3: **2026-03-25**
- D1 PROJECTSTATUS_D1: **2026-02-22**
- Branch laatste commit: 2026-04-25

Niet fout — modellen rijpen in eigen tempo — wel asynchroon. Een
release-kalender (cat D5) zou de update-status zichtbaar maken.

**H3. D2 → C1 hernoeming: ✓ consistent doorgevoerd.**
PROJECTSTATUS markeert het, README en protocol gebruiken nieuwe naam,
geen restanten van D2 in de hoofdstroom.

---

## Categorie I — Modelspecifieke gezondheid (steekproef)

**Naamconventie:** alle modellen hebben `README_<X>.md`,
`EPICS_<X>.md`, `PROJECTSTATUS_<X>.md` (underscore, geen spatie of dash). ✓

| Model | Status | Volgende stap | Templates | Tooling |
|---|---|---|---|---|
| L3 NSkiV | v11.3, 51N/176E | NSkiV-documenten verwerken | ✗ ontbreekt | 13 scripts |
| D1 Sportdeelname | v2.3.0, 69N/114E | E05 GEXF-tool afronden | n.v.t. | scripts via L3-pattern niet zichtbaar |
| L2 AVV | v1.0, 32/63 stories | Slider-simulatietool | ✗ ontbreekt | 7 AVV-scripts |
| A_ Architectuur | Protocol v0.3, ref-impl. | E07 Validatie (wacht op WP4) | n.v.t. | pipeline + run_case |
| C1 Data-Informed | Geherpositioneerd | E01 S5 synthese | n.v.t. | niet gecheckt |
| L1 Vermogensmodel | Theoretisch compleet | EPICS harmoniseren | ✓ aanwezig | basaal (2 scripts) |

**I1. L1: ✓ templates aanwezig.**
`L1_.../templates/Case capture canvas.md`, `Case respons template
vermogensmodel.md`, `WERKPLAN - Batch Vermogens Documentatie.md`. Dit is
het patroon dat de verkenning §8.1 voor L3 als actie noemde.

**I2. L3: ✗ templates/-map ontbreekt.**
Direct GET op `L3_NSkiV/templates` levert 404. De verkenning §8.1-actie
("L3 casus-capture + casus-respons templates naar model van L1") is open.

**I3. D1: ⚠ stories-discrepantie.**
`D1_/PROJECTSTATUS_D1.md` zegt **39/90 stories**;
`PROJECTSTATUS_Modelbouw.md` zegt **39/117**. De getallen
verschillen — mogelijk verschillende telling (open versus alle stories,
of E05/E11 wel/niet meegerekend). Niet kritiek, wel symptoom van datum-
divergentie en ontbreken van centrale story-checker.

**I4. D1: ⚠ route C/D in atlas niet operationeel.**
Volgens PROJECTSTATUS alleen Gephi Lite-inspectie; pipeline-route via
A_/scripts/pipeline.py, niet bij D1 zelf. Voor LLM-reasoning over casus
(route C) is het dus aangewezen op Graaf Zeppelin — wat de G3-verhouding
nog dringender maakt.

**I5. L2: ⚠ stock-vs-slider-toets niet zichtbaar gestart.**
Verkenning §8.1, B9: de architectuurnotitie geeft de methodiek; uitvoering
is een review-ronde. Niet gemarkeerd in PROJECTSTATUS als actie.

**I6. A_: ✓ protocol + pipeline-runnable + realistic case-output operationeel.**
Stevigste model qua route-D-rijpheid.

---

## Drie vervolgstappen, geprioriteerd op ROI

### 1. CLAUDE.md op root van atlas (kritiek, ½ dag werk)

Bevat:
- **Taalconventie**: NL voor docs, identifiers Engels of NL
  (NL als domein-inhoudelijk).
- **Story-Kanban-workflow** met file-naming-patronen
  (`S##-##-korte-naam.md`).
- **A_ als protocol-eigenaar**: protocol-changes lopen via A_, niet via
  individuele modellen.
- **Commit-conventies** (feat/fix/docs..., NL body, story-ID-referentie).
- **Niet-doen-lijst**:
  - Geen protocol-changes buiten A_.
  - Geen 1-op-1 mapping forceren tussen D1 en L2 (verschillende
    afbakeningen op hetzelfde niveau).
  - Niet `_archief`-mappen wijzigen.
  - Geen evidence-claims zonder `ref_id`.
  - Geen stille slider-naamafwijkingen tussen modellen.
- **Verwijzingen** naar `00_verkenning-v2.md` (coördinatie) en
  `docs/leeswijzer.md` (snelstart).

Zonder dit moet elke sessie ~30 min uitvinden wat al bekend is.

### 2. Cross-model slider-register als eerste levend register (medium, 1 dag)

Een markdown-tabel of kleine YAML in
`A_/model/cross-level/cross_model_sliders.md` (of vergelijkbaar pad), met
per slider:
- Naam.
- Type (interventie / calibratie / context).
- Schaal (typisch [0, 1]).
- Default per model.
- Expliciete afwijkings-notes.

Begin met de 17 sliders uit `E05_S03_slider_inventaris.md` als
bronlijst en breid uit met L2/L3/D1-sliders. Hiermee wordt verkenning
§8.2 operationeel-gemaakt; dit is ook fundament voor toekomstige
cross-level-validatie.

### 3. Atlas ↔ Graaf Zeppelin verhoudingsverklaring (klein, 1-2 uur)

Eén alinea in `D1_/README_D1.md` of `PROJECTSTATUS_D1.md`:

> *D1 JSON's hier zijn de spec-bron. Graaf Zeppelin
> ([github.com/maxonamission/graaf_zeppelin](...)) laadt een afgeleide
> graph voor LLM-reasoning (route C). Synchronisatie: handmatig bij elke
> D1-versiebump, met checksum of versie-tag in beide repo's. Atlas blijft
> leidend voor structuur; Graaf Zeppelin blijft leidend voor runnable
> implementatie.*

Voorkomt stille divergentie. Lage moeite, hoge clarity-winst.

---

## Bonus-stappen (lagere ROI, kleine moeite)

- **L3 templates/-map kopiëren van L1-pattern.**
  Kopieer `L1_.../templates/Case capture canvas.md` en `Case respons
  template vermogensmodel.md` naar `L3_NSkiV/templates/`, herschrijf
  naar bond-niveau (strategische horizon, klimaatdruk, demografie).
  Opent route A voor L3.

- **Lichte CI: markdownlink-checker + check_story_status.py-port.**
  `.github/workflows/check.yml` met één job die:
  1. Alle markdown-links valideert.
  2. Een geporte story-status-checker draait (uit Graaf Zeppelin).
  Geen zware suite; alleen signaal-functie.

- **Protocol-validator-skelet `_scripts/validate_protocol.py`.**
  Per JSON-graaf controleren of `edge_type`, `curve_type`, `node_class`
  binnen v0.3-vocabulaire vallen (8 / 4 / 2). Geeft houvast bij
  toekomstige protocol-bumps en is voorwaarde voor een betekenisvolle
  CI.

---

## Niet meegenomen (volgende ronde)

- **Inhoudelijke story-controle per model** (toegezegd: stories
  inhoudelijk meenemen).
- **L2 stock-vs-slider toets-uitvoering** (vereist domein-review).
- **Verweesde-link-scan** (vereist grep over hele atlas).
- **Pipeline-empirische-validatie** (wacht op WP4-data per
  PROJECTSTATUS).

---

*Controle uitgevoerd vanuit Graaf Zeppelin sessie. Atlas zelf is niet
gewijzigd; deze rapportage is feedback. Wijzigingen in atlas (CLAUDE.md
of registers) gaan via de atlas-repo zelf, niet via deze.*
