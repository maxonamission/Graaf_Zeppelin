# Controle inrichting `codebase_atlas` — 25 april 2026

**Branch gecontroleerd:** `claude/import-action-plan-OSoWH`
**Vergeleken met:** vorige snapshot (zelfde branch, ongedateerd) en
verkenning-v2 §8 harmonisatie-voorstellen.
**Toegang:** WebFetch op publieke URLs (GitHub-MCP is restricted tot
graaf_zeppelin).

---

## Samenvatting in één blik

| Categorie | Status | Belangrijkste observatie |
|---|---|---|
| A. Repo-werkvloer voor LLM | ⚠ | leeswijzer ✓, README ✓, CLAUDE.md ✗ |
| B. Story-hygiene en -tooling | ✗ | geen story-checker; alleen migratie-scripts |
| C. Protocol-governance | ⚠ | protocol v0.3 actueel, maar geen validator/procedure |
| D. Cross-project registers | ⚠ | slider-inventaris bestaat (binnen A_), rest ontbreekt |
| E. CI / kwaliteitsbewaking | ✗ | geen `.github/`, geen `.pre-commit` |
| F. Cross-level relaties | ✓ | `cross_level_edges.json` aanwezig |
| G. Verhouding tot Graaf Zeppelin | ✗ | geen eigenaarschap-statement |
| H. Documentatie-coherentie | ✓ | versies en taal consistent over hoofdstukken |
| I. Modelspecifieke gezondheid | ✓ | per PROJECTSTATUS allemaal levend |

**Eindconclusie:** protocol-laag en cross-level-architectuur staan
solide; werkvloer-laag (CLAUDE.md, registers, CI, governance-procedures)
is grotendeels nog open. Drie gerichte vervolgstappen onderaan.

---

## Categorie A — Repo-werkvloer voor LLM

**A1. CLAUDE.md op root: ✗ ontbreekt nog.**
Een directe `raw.githubusercontent.com/.../CLAUDE.md` levert 404. Zonder
dit moet elke Claude-sessie opnieuw uitvinden welke conventies gelden.

**A2. `docs/leeswijzer.md`: ✓ aanwezig en aangepast.**
Het origineel is bewaard als `docs/leeswijzer-zip-origineel.md`. Goed
versiebeheer.

**A3. Top-level `README.md`: ✓ aanwezig.**
Beschrijft protocol, hiërarchie, naamgeving, Kanban. Sluit aan op de
leeswijzer. Geen inhoudelijke conflicten.

---

## Categorie B — Story-hygiene en -tooling

**B1. Story-checker in `_scripts/`: ✗ ontbreekt.**
`_scripts/` bevat alleen `migrate_frontmatter.py` en `rename_stories.py`.
Geen equivalent van Zeppelins `check_story_status.py`. Zonder dit is
status-drift tussen `EPICS_*.md` en `stories/<status>/` niet bewaakt.

**B2. Story-mapstructuur per model: ✓ aannemelijk.**
A_ heeft een `stories/` submap; mag aangenomen worden dat de andere
modellen vergelijkbaar gestructureerd zijn (niet per model
gecontroleerd).

**B3. EPICS ↔ file-locatie sync: ⚠ niet getoetst.**
Vereist een steekproef per model — zonder checker handmatig werk.

---

## Categorie C — Protocol-governance

**C1. `gedeeld_protocol.md`: ✓ actueel.**
Versie **0.3** (geëffectueerd 25 maart 2026). Bevat 8 edge-types
(`enables`, `threatens`, `requires`, `modulates`, `competes_with`,
`improves`, `shapes`, `erodes`), 4 curve-types (`LINEAR`, `SATURATING`,
`THRESHOLD`, `INVERTED_U`), evidence-schaal A/B/C.

> Opmerking: in de architectuurnotitie (en eerder gerapporteerd)
> stond `THRESHOLD_LOGISTIC`; protocol gebruikt korter `THRESHOLD`.
> Geen probleem zolang het consistent is binnen het protocol.

**C2. Protocol-validator: ✗ niet zichtbaar.**
`A_.../scripts/` bevat `pipeline.py`, `run_realistic_case.py`,
`realistic_case_output.json` — geen validator die node_class /
edge_type / curve_type / evidence-schaal afdwingt.

**C3. Protocol-change-procedure: ✗ niet expliciet.**
`meta-architectuur.md` is governance-als-kaart, niet als regelboek.
Wie protocol-changes voorstelt, hoe modellen impact-assessed worden,
en hoe backward-compat gehandhaafd is — niet beschreven.

**C4. Versionering: ⚠ versienummer wel, release-notes niet.**
v0.3 staat in het document; een `CHANGELOG.md` of release-notes-mapje
ontbreekt.

---

## Categorie D — Cross-project registers (verkenning §8.2)

**D1. Cross-model slider-register: ⚠ deels.**
`A_.../docs/E05_S03_slider_inventaris.md` is een 17-sliders-inventaris,
maar context is GVM (referentie-implementatie). Een expliciete cross-
model lijst die per slider aangeeft "in welke modellen, met welke
defaults, met welke afwijkingen" ontbreekt.

**D2. Stock-node-register per niveau: ⚠ verspreid.**
De architectuurnotitie noemt stock-kandidaten in proza; een gedeelde
lijst (per L2/L3 een document met de stocks) ontbreekt als zelfstandig
artefact.

**D3. Domein-taxonomie-mapping: ✗ niet gevonden.**
Geen document dat D1's 9 domeinen en GVM's 5 dimensies expliciet aan
elkaar koppelt.

**D4. Evidence-bibliografie gedeeld: ✗ niet gevonden.**
Geen centrale `references.bib`-equivalent. Evidence per edge zit in
modelmappen.

**D5. Protocol-release-kalender: ✗ niet gevonden.**
Geen overzicht "welke modellen op welke protocolversie".

---

## Categorie E — CI / kwaliteitsbewaking

**E1. `.github/workflows/`: ✗ map bestaat niet (404).**

**E2. `.pre-commit-config.yaml`: ✗ bestaat niet (404).**

**E3. `.gitignore`: ✓ aanwezig.**
Inhoud niet gecontroleerd.

**Consequentie:** wijzigingen in atlas worden niet automatisch gevalideerd.
Voor een meta-repo waar zes modellen samenkomen is dit een lacune die
groeit naarmate er meer cross-cutting werk plaatsvindt.

---

## Categorie F — Cross-level relaties

**F1. `cross_level_edges.json`: ✓ aanwezig.**
Pad: `A_.../model/cross-level/`. Naast `pipeline_output.json`. PROJECT-
STATUS noemde "55 cross-level edges" — aannemelijk dat dat hier zit.

**F2. L2 stock-vs-slider toets: ⚠ niet zichtbaar als afzonderlijk
artefact.**
PROJECTSTATUS L2 vermeldt "v1.0 gevalideerd; 32/63 stories af" en als
volgende stap "E05 Slider-simulatietool starten" — de stock-vs-slider-
toets uit de architectuurnotitie is niet expliciet gemarkeerd.

**F3. Niveau-autonomie: niet direct toetsbaar.**
Vereist code-inspectie van pipeline en model-loaders. Architecturale
positie is helder; uitvoering aannemelijk maar niet bewezen.

---

## Categorie G — Verhouding tot Graaf Zeppelin (D1)

**G1. `D1_.../`-map status: niet expliciet beschreven.**
De map bestaat in atlas; PROJECTSTATUS noemt "v2.3.0 kwantitatief; 39/117
stories af" — suggereert dat atlas een levende kopie is, niet alleen
spec.

**G2. Eigenaarschap-statement: ✗ niet gevonden.**
Geen document dat zegt "atlas/D1_ is leidend voor structuur, Graaf
Zeppelin is leidend voor runnable implementatie" of andersom.

**G3. Synchronisatie-procedure: ✗ niet gevonden.**
Risico op divergentie als beide bewegen.

---

## Categorie H — Documentatie-coherentie

**H1. Hoofdstukken consistent: ✓.**
`00_verkenning-v2.md`, `docs/leeswijzer.md`, `README.md`,
`meta-architectuur.md`, `PROJECTSTATUS_Modelbouw.md` hanteren dezelfde
taal en versies (protocol v0.3).

**H2. Verweesde verwijzingen: ⚠ niet grondig getoetst.**
Steekproef noodzakelijk; D2 → C1-rename is in PROJECTSTATUS gemarkeerd,
maar of alle verwijzingen meegegaan zijn, is niet vastgesteld.

**H3. Datums consistent: ✓.**
PROJECTSTATUS-datum (25 mrt 2026), protocol-datum (25 mrt 2026), branch
laatste update (25 apr 2026) — geen conflicterende ouderdom.

---

## Categorie I — Modelspecifieke gezondheid (uit PROJECTSTATUS)

| Model | Status | Volgende stap | Gezondheid |
|---|---|---|---|
| L3 NSkiV | v11.3 operationeel; 51 nodes, 176 edges | NSkiV-documenten verwerken | ✓ levend |
| D1 Sportdeelname | v2.3.0; 39/117 stories | E05 GEXF-tool afronden | ✓ levend |
| L2 AVV | v1.0 gevalideerd; 32/63 stories | Slider-simulatietool | ✓ levend |
| A_ Architectuur | Protocol v0.3, ref-impl. concept | E07 Validatie (wacht op WP4) | ✓ levend |
| C1 Data-Informed | Geherpositioneerd als capability | E01 S5 synthese | ✓ levend |
| L1 Vermogensmodel | Theoretisch compleet | EPICS harmoniseren met MLS | ⚠ niet gevalideerd |

Steekproef per model voor templates/casus-capture is niet uitgevoerd —
hoort bij de volgende controle-ronde wanneer stories inhoudelijk
worden meegenomen.

---

## Wat is er bijgekomen sinds vorige snapshot?

**Geen verschillen geconstateerd in skelet.** Top-level mappen,
top-level bestanden, `_scripts/`, `docs/` zijn identiek aan de vorige
check. PROJECTSTATUS is bijgewerkt en het protocol staat op v0.3
geëffectueerd 25 maart 2026.

**Wat nog open is sinds vorige feedback:**
- CLAUDE.md (cat A) — niet aangemaakt.
- Story-checker (cat B) — niet aangemaakt.
- Protocol-validator (cat C) — niet aangemaakt.
- Cross-project registers (cat D) — niet aangemaakt.
- CI / pre-commit (cat E) — niet aangemaakt.
- D1 eigenaarschap-statement (cat G) — niet aangemaakt.

---

## Drie vervolgstappen, ranked op ROI

### 1. CLAUDE.md op atlas-root (hoogste impact, lage kosten)

Inhoud minimaal:
- Taalconventie (NL docs, mogelijk EN identifiers).
- Protocol-governance: A_ beheert het protocol; wijzigingen lopen via
  daar.
- Story-workflow: Kanban-mappen + EPICS-status synchroon houden.
- Commit/branch-conventies (feat/fix/docs..., branch-naam-patroon).
- Niet-doen-lijst (geen stille slider-naamafwijkingen, geen protocol-
  wijzigingen buiten A_, geen evidence-claims zonder bron).
- Verwijzing naar `00_verkenning-v2.md` als coördinatiedocument en
  naar `docs/leeswijzer.md` als snel-startpunt.

Schat: 1 dag werk inclusief reviewronde. Geeft elke toekomstige
LLM-sessie een vliegende start.

### 2. Story-hygiene-checker porten + minimale CI (middelhoge impact, lage kosten)

- Port `scripts/check_story_status.py` uit Graaf Zeppelin naar
  atlas `_scripts/`. Aanpassing: geen Python-package-context, alleen
  bestandssysteem-walk.
- `.github/workflows/check.yml`: één job die de checker draait op alle
  modellen.
- Optioneel `.pre-commit-config.yaml` met markdownlint + checker.

Schat: halve dag. Voorkomt status-drift; geeft signaal-functie naar
contributors.

### 3. Cross-project registers in `A_/registers/` (middelhoge impact, hogere kosten)

Initieel als skelet-bestanden, te vullen door modeleigenaren:
- `cross_model_sliders.md` — tabel slider × model × default × afwijking.
- `stock_register.md` — per niveau (L2, L3) de erkende stocks.
- `domein_mapping.md` — D1 9-domeinen ↔ GVM 5-dimensies.
- `evidence_bibliography.md` — gedeelde literatuur, mogelijk BibTeX.
- `protocol_compatibility.md` — welk model op welke protocolversie.

Skelet aanmaken kost een dag; vullen kost weken en is per register
een eigen story. Maar zonder skelet komt het er niet.

---

## Niet meegenomen (voor volgende ronde)

- Inhoudelijke story-controle per model (toegezegd door gebruiker).
- L2 stock-vs-slider toets-uitvoering (vereist domein-review).
- Verweesde-link-scan (vereist grep over hele atlas).
- Pipeline-empirische-validatie (wacht op WP4-data per PROJECTSTATUS).

---

*Controle uitgevoerd vanuit Graaf Zeppelin sessie. Atlas zelf is niet
gewijzigd; deze rapportage is feedback. Wijzigingen in atlas (CLAUDE.md
of registers) gaan via de atlas-repo zelf, niet via deze.*
