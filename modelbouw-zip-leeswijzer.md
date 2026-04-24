# Leeswijzer — Modelbouw.zip

**Doel van dit document:** een LLM (Claude Code of vergelijkbaar) in
een andere repo snel laten begrijpen wat er in `Modelbouw.zip` zit,
welke conventies gelden, en waar je moet kijken voor welke vraag.
Dit is geen inhoudelijke samenvatting — voor die rol zie
`modelbouw-verkenning-v2.md` in dezelfde repo.

---

## 1. Wat is Modelbouw?

Modelbouw is een ecosysteem van zes causale modellen rond sport en
organisatievermogens, met een eigen modulaire architectuur (protocol
v0.3) die de zes modellen bindt via representatie-afspraken maar
inhoudelijke vrijheid laat.

De zes modellen opereren op drie niveaus:

- **L1** — individueel (micro)
- **L2, D1, C1** — organisatie / vereniging / specifiek domein (meso)
- **L3** — bond / sector (macro)

Plus één protocol-laag **A_** die de grammatica beheert.

---

## 2. Top-level structuur

```
Modelbouw/
├── A_Modulaire Modelarchitectuur/   ← protocol v0.3 + referentie-impl.
├── L1_Ontwerp en Onderzoek Vermogensmodel/
├── L2_Affectief Vitale Vereniging/
├── L3_NSkiV/
├── D1_Ontwerp en Onderzoek Sportdeelnamemodel/
├── C1_Ontwerp en Onderzoek Capability Model Data-Informed Werken/
├── README.md
├── PROJECTSTATUS_Modelbouw.md
├── meta-architectuur.md
├── Overzicht en opruimadvies Modelbouw.md
└── archief/
```

Elk model volgt ongeveer dezelfde interne structuur:

```
<model>/
├── README_<model>.md            ← start hier per model
├── PROJECTSTATUS_<model>.md     ← rijpheid, recent werk
├── EPICS_<model>.md             ← epic/story-backlog (Kanban)
├── docs/                        ← inhoudelijke notities, specs
├── model/ of graph/ of data/    ← het causale model (JSON/YAML)
├── stories/                     ← backlog/doing/done
├── scripts/                     ← validators, converters
├── agents/ (L1) of templates/   ← agent-briefings, casus-templates
└── archief/
```

---

## 3. De zes modellen in één blok

### A_ — Modulaire Modelarchitectuur (protocol-laag)

Beheert het gedeelde protocol (v0.3). Bevat referentie-implementaties
**GVM** (Generiek Vermogensmodel, meso) en **CSM**
(Crisissystematiekmodel, macro) plus een werkende deterministische
`pipeline.py` (~630 regels, micro→meso→macro).

- **Start:** `A_.../docs/Briefing_Modulaire_Modelarchitectuur.md`
- **Protocol:** `A_.../model/protocol/gedeeld_protocol.md`
- **Kernarchitectuur:**
  - `A_.../docs/architectuurnotitie_stock_nodes_sliders_cultuur.md`
  - `A_.../docs/architectuurnotitie_l2_capabilities.md`
  - `A_.../docs/E05_S03_slider_inventaris.md`
- **Specificaties referentie-implementaties:**
  `GVM_Specificatie.md`, `CSM_Specificatie.md`

### L1 — Vermogensmodel (individueel)

Micro-niveau: zelfvitaliserend vermogen, emotieregulatie, zelfzorg,
motivatie. Dominante use-case: **authoring + agent-briefing** (LLM
redeneert met een casus over een individu).

- **Start:** `L1_.../README_L1.md`
- **Agent-briefings:** `L1_.../agents/AGENT-BRIEFING-TEMPLATE-Vermogen.md`
  en de vier vermogen-specifieke agenten.
- **Casus-templates:** `L1_.../templates/` (capture + respons).

### L2 — Affectief Vitale Vereniging (AVV)

Meso-niveau: 21 vermogens van een sportvereniging. Runnable in
prototype-vorm.

- **Start:** `L2_.../README` (pad varieert)
- Bevat een eigen graph met vermogens, sliders, edges en een
  doorrekenmechanisme.

### L3 — NSkiV (Nederlandse Ski-Vereniging, bond)

Macro-niveau: strategisch bondsmodel (22 nodes), inception-fase.
Dominante focus: scenario-denken met klimaatdruk, demografie,
normatieve druk als sliders.

- **Start:** `L3_.../README` en
  `L3_.../scenarios/NSkiV_Scenario_Framework_Context_Sliders.md`

### D1 — Sportdeelnamemodel (beleidsverkenner)

Meso-niveau, 69 nodes, 108 edges over 9 domeinen. Dit is het model
achter **Graaf Zeppelin** (beleidsverkenner-webapp). Route A+C:
authoring en LLM-reasoning over casus.

- **Start:** `D1_.../README`
- Het actieve graph-bestand wordt door Graaf Zeppelin geladen
  (zie die repo's `data/models/sportdeelname_graph.json`).

### C1 — Capability Model Data-Informed Werken

Meso-niveau, specifiek thematisch domein (data-informed beslissen in
een sportorganisatie). Vroege fase.

- **Start:** `C1_.../README`

---

## 4. Protocol v0.3 — de gedeelde grammatica

Alle modellen volgen (of bewegen richting) deze afspraken:

**Node-types:**
- `node_class: regular` — standaard.
- `node_class: stock` — accumulerende toestandsvariabele, vereist
  `change_rate` (`slow` / `medium` / `fast`).

**Edge-types** (gesloten vocabulaire, 8 stuks):
`enables`, `constrains`, `shapes`, `threatens`, `erodes`,
`modulates`, `builds`, `drives` (exacte lijst: zie
`A_.../model/protocol/gedeeld_protocol.md`).

**Curve-types** (4 stuks):
`LINEAR`, `SATURATING`, `INVERTED_U`, `THRESHOLD_LOGISTIC`.

**Evidence-schaal:**
- `A` — sterk (meta-analyse / reviews)
- `B` — matig (empirische studies)
- `C` — zwak / expert judgement

**Sliders**, drie typen:
- **Interventie** — keuze van de gebruiker (bv. investering in
  cultuur).
- **Calibratie** — parameter-onzekerheid voor robustness-checks.
- **Context** — externe omgeving of stock-van-niveau-erboven.

---

## 5. Twee sleutelprincipes

### 5.1 Stock-vs-slider (architectuurnotitie v0.2)

> Sliders zijn **extern** (door gebruiker ingesteld, geen node in de
> graph). Stocks zijn **intern** (accumuleren over tijd, hebben
> in- en uitgaande edges).

Functie ≠ oorsprong: iets kan modererend zijn *en* toch een stock
(bv. psychologische veiligheid, organisatiecultuur).

### 5.2 Cross-level principe

> **Een stock node op niveau N wordt slider op niveau N-1.**

Wat de organisatie intern opbouwt, ervaart het individu als gegeven
context. Dit maakt slider-lijsten per niveau *afleidbaar* uit de
stock-lijsten van het niveau erboven, *voor zover relevant* voor
de vragen van dat niveau. Niveau-autonomie blijft het primaat:
elk niveau moet zelfstandig werken zonder de invulling van het
niveau erboven te kennen.

Bron: `A_.../docs/architectuurnotitie_stock_nodes_sliders_cultuur.md`.

---

## 6. Vier use-case routes

Modellen zijn op verschillende manieren nuttig. Onderscheid:

- **Route A — Authoring / agent-briefing**: LLM-agent met
  domeincontext (L1, L3-inception, D1-auteursmodus).
- **Route B — Model-als-ground-truth**: gevalideerd kennismodel
  voor domeinexperts (GVM als referentie, L2 in rijping).
- **Route C — LLM-reasoning over casus**: LLM redeneert over
  concrete casus met modelraadpleging (D1/Graaf Zeppelin, L2
  op termijn).
- **Route D — Deterministische pipeline**: reproduceerbare
  micro→meso→macro-doorrekening (A_/pipeline.py).

Patroon: A → B → C → D, maar modellen rijpen in eigen tempo.

---

## 7. Leesvolgorde voor een LLM (eerste sessie)

Als je voor het eerst Modelbouw ontmoet, lees in deze volgorde:

1. `Modelbouw/README.md` — project op één pagina.
2. `Modelbouw/PROJECTSTATUS_Modelbouw.md` — waar staat elk model.
3. `A_.../model/protocol/gedeeld_protocol.md` — de grammatica.
4. `A_.../docs/architectuurnotitie_stock_nodes_sliders_cultuur.md`
   — het kernprincipe dat alle modellen raakt.
5. `A_.../docs/E05_S03_slider_inventaris.md` — het slider-contract.
6. `README_<model>.md` van het model dat relevant is voor jouw vraag.

Voor cross-model denken lees daarnaast:

- `modelbouw-verkenning-v2.md` (in Graaf Zeppelin) — coördinatie
  tussen de zes modellen.

---

## 8. Conventies

- **Taal**: documentatie in **Nederlands**, identifiers in code mogen
  Engels of NL zijn (NL als het domein-inhoudelijk is:
  `bond_influence`, `slider_sensitivity`).
- **Encoding**: UTF-8 zonder BOM.
- **ID-schema**: zie per model (D1/Graaf Zeppelin heeft
  `<domein>_<node>` Vorm A; andere modellen variëren; protocol
  harmoniseert dit nog).
- **Stories** (per model): `stories/backlog/`, `stories/doing/`,
  `stories/done/`. Overzicht in `EPICS_<model>.md`.
- **Semver** op protocolversie (v0.3 op moment van zippen).
- **Evidence** altijd in `A/B/C` — niet vrije tekst.

---

## 9. Waar vind ik wat? (quick lookup)

| Vraag | Locatie |
|---|---|
| Wat is het protocol? | `A_.../model/protocol/gedeeld_protocol.md` |
| Wat zijn de edgetypes/curvetypes? | idem, plus `GVM_Specificatie.md` |
| Hoe zit stock-vs-slider? | `A_.../docs/architectuurnotitie_stock_nodes_sliders_cultuur.md` |
| Welke sliders bestaan? | `A_.../docs/E05_S03_slider_inventaris.md` |
| Hoe rekent de pipeline? | `A_.../docs/E06_S01_pipeline_architectuur.md` + `pipeline.py` |
| Hoe ziet een L1-casus eruit? | `L1_.../templates/Case capture canvas.md` + `Case respons template vermogensmodel.md` |
| Hoe brieft men een L1-agent? | `L1_.../agents/AGENT-BRIEFING-TEMPLATE-Vermogen.md` |
| Wat is GVM vs CSM? | `A_.../docs/GVM_Specificatie.md`, `CSM_Specificatie.md` |
| Projectstatus per model | `<model>/PROJECTSTATUS_<model>.md` |
| Cross-model advies | `modelbouw-verkenning-v2.md` (Graaf Zeppelin) |

---

## 10. Niet-doen (veelgemaakte fouten)

- **Niet aannemen dat alle modellen protocol v0.3 volledig
  implementeren.** Adoption is incrementeel; sommige modellen zitten
  op v0.2 of eerder.
- **Niet één slider-lijst opleggen aan alle modellen.** Slider-
  relevantie is niveau- en casus-afhankelijk (§4.3 in de verkenning).
- **Niet L2 als afgeleide van L3 behandelen.** Niveau-autonomie: L2
  werkt zonder L3-invulling.
- **Niet de 69-nodes van D1 proberen te mergen met de 21-vermogens
  van L2.** Ze beschrijven hetzelfde niveau maar met verschillende
  afbakeningen. Co-existentie, geen consolidatie.
- **Niet de pipeline-gewichten als empirisch valid aannemen.** Ze
  zijn theoretisch; validatie staat op de roadmap.
- **Niet protocol-wijzigingen doen buiten A_ om.** Governance loopt
  via de protocol-laag, niet via individuele modellen.

---

## 11. Snelle signalen voor "welke fase staat dit model?"

Kijk in `PROJECTSTATUS_<model>.md`. Indicatieve signalen:

- **Inception**: README bestaat, nodes nog niet geformaliseerd,
  weinig of geen stories in `done/`.
- **Rijpend (route A)**: agent-briefings + casus-templates aanwezig,
  causaal model in concept.
- **Rijp (route B)**: evidence-kolom gevuld, expert-review gedaan.
- **Runnable (route C/D)**: graph in JSON/YAML, scripts werken,
  pipeline of LLM-integratie operationeel.

---

*Deze leeswijzer is geschreven voor een LLM-assistent die
`Modelbouw.zip` uitgepakt tegenkomt. Het is geen inhoudelijke
samenvatting — voor coördinatie-advies tussen de zes modellen zie
`modelbouw-verkenning-v2.md` (ook in deze branch).*
