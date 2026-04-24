# Verkenning — Modellen-ecosysteem Modelbouw

**Status:** Verkennend advies, geen vastgelegde route.
**Doel:** Routes in beeld brengen naar een gezond systeem van zes causale netwerkmodellen (L1, L2, L3, D1, C1, A_), met respect voor wat er inhoudelijk al staat.
**Datum:** 2026-04-23
**Schrijver:** Claude (in opdracht van Max), op basis van uitgepakte `Modelbouw/`-folder + ~6 parallelle deep-reads.

---

## 1. Kader

### 1.1 De modellen zijn de magie

De modellen in Modelbouw zijn niet de applicatie; ze zijn **inhoudelijk
werk** — literatuur-onderbouwde causale netwerken die in verschillende
toepassings­vormen nuttig kunnen zijn. De applicatie (of de LLM, of de
data-koppeling) is een *consumer*. Dat bepaalt hoe je over integratie
nadenkt: niet "hoe plak ik ze aan elkaar vast?", maar "hoe zorg ik dat
elk model naar de use-case waar het voor bedoeld is goed ontsloten is,
zonder dat ik de modellen zelf kapot maak?"

### 1.2 Vier use-case-routes

Uit het gesprek met Max kristalliseerden vier archetypes uit waarin een
model nuttig wordt:

- **Route A — LLM-context met casus + kalibratie-sliders.** Gebruiker
  vult een situatie in een capture-formulier (observaties +
  slider-instellingen), LLM redeneert langs nodes en edges naar een
  analyse/aanbeveling. Primair voor L1; beproefde template bestaat.
  Sliders functioneren hier als **kalibratie** (wat is de context van
  de case?), niet als interventie.
- **Route B — Interactieve app.** Gebruiker manipuleert sliders als
  beleids-interventies, krijgt simulatie-uitkomsten terug. Primair
  voor D1 via Zeppelin; in potentie voor L2 en L3.
- **Route C — Koppeling aan echte data.** Node-indicatoren krijgen een
  waarde uit ledensystemen, jaarverslagen, KPI-dashboards of
  vragenlijsten. Primair voor D1 (KNSB-data) en L3 (periodieke
  bond-voeding); secundair voor L2.
- **Route D — Onderzoeks-archief en reproduceerbaarheid.** Het model
  is een artefact: versioneerbaar, citeerbaar, literatuur-verbonden,
  reproduceerbaar. Voor elk model relevant, vooral als wetenschappelijke
  onderbouwing of als evaluatie-instrument.

Deze routes zijn **niet exclusief**: één model kan meerdere routes
ondersteunen, op verschillende momenten of voor verschillende
doelgroepen.

### 1.3 Wat ik bewust níet doe in dit document

- Geen "niveau A/B/C-integratie"-keuze. Dat bleek te vroeg gevraagd;
  het document laat ruimte.
- Geen architectuur-voorschrift. Je kunt na lezing nog redelijkerwijs
  verschillende kanten op.
- Geen prioritering van modellen onderling. Prioritering komt pas bij
  het uitvoeren van een route — niet bij het bestaansrecht van een
  model.

---

## 2. Per-model snapshot

### L1 — Vermogensmodel (micro: individu)

**29 nodes · 99 edges · 4 sliders · 6 clusters · 204 literatuur-bronnen.**

Theoretisch compleet en methodologisch rigoureus. Edges evidence-gerangschikt
(61× A-level, 34× AUDIT, 4× B). Curve-bibliotheek uitgewerkt (LINEAR,
SATURATING, INVERTED_U, THRESHOLD_LOGISTIC). Eigen edge-typologie
(FOUNDATIONAL/MEDIATING/SOCIAL_REGULATORY/STRUCTURAL/FEEDBACK).

**Dominante route:** A (LLM-context). Case Capture Canvas + Case Respons
Template zijn operationeel als template-set; nog geen system-prompt
die ze aan het model + LLM koppelt. Agent-briefings (authoring-kant) zijn
een aparte LLM-use: zij bouwen het model uit, de case-templates passen
het toe.

**Secundair:** D (onderzoeks-archief — alles is er). B en C spelen niet
actief.

**Onaf:** geen empirische gewichts-kalibratie; interventie-catalogus
(MX-serie) staat naast de graaf in plaats van eraan gekoppeld.

### L2 — Affectief Vitale Vereniging (meso: organisatie)

**21 nodes · 76 edges · 8 sliders · 97 literatuur-bronnen · 6
verenigingsprofielen · 15 interventiepakketten.**

v1.0 gevalideerd. Eigen edge-typologie (FOUNDATIONAL/MEDIATING/MODERATING),
19 JSON-bestanden onder `model/` voor A-E-reeksen (vermogens, edges,
sliders, uitkomsten, interventies, pakketten, profielen, drukanalyses,
vragenlijst, scoring, matching).

**Wat L2 uniek heeft:** een complete **diagnose-pipeline**. Vragenlijst
(78 items, Likert) → scoringsmodel → profielmatching tegen zes types
→ interventieadvies. Getest (6/6 profielmatching-tests groen).

**Dominante route:** A + B gecombineerd. De diagnostiekgids is
praktijkklaar (route A), een webtoepassing is geplande vervolgstap
(E07, backlog). Route C speculatief (Vitaliteitsindex, NOC*NSF-data
genoemd maar niet uitgewerkt).

**Onaf:** geen empirische veldtoetsing (E08 backlog), geen
git-versiebeheer (E01-S06 bewust geparkeerd tot v1.1), 6 citatie-issues
geaccepteerd.

### L3 — NSkiV (macro: bondsstrategie)

**51 nodes · 176 edges · 5 scenario-assen · 900 literatuur-bronnen ·
4 uitgewerkte scenario's.**

v11.3, actueel. Kwalitatief edge-vocabulaire (enables/drives/
constrains/threatens/requires/serves/depends_on/competes_with). De
vijf sliders zijn **context-parameters** (wat-is-de-wereld?), niet
kalibratie of interventie: klimaatdruk, economisch klimaat, digitale
versnelling, maatschappelijke verwachtingen, gedragsverandering. Geen
0-1-waarden maar posities als "geleidelijk / versneld / disruptief".

**Werkende data-voeding bestaat al:** C1/C2/C3-classificatie van
organisatie-documenten is operationeel (eerste snapshot ingevuld
vanuit Visiedocument NSkiV). Kwartaalprotocol gedefinieerd.

**Dominante route:** A + B (strategisch gesprek). Beleidsplan 2026-2030
afgerond (52 pagina's), managementsamenvatting + gespreksleidraad +
toelichting-systeemmodel + vergelijkingsrapport. Route C is
raamwerk-klaar maar nog niet kwantitatief gevoed. Route D sterk ontwikkeld
(literatuurregister, thema-rapporten T01-T14).

**Onaf:** geen git (S01-02 open), geen interactieve slider-app
(S05-03 geparkeerd omdat Max eigen app bouwt), 60% edges nog zonder
`lit_ids`, geen expliciete L3↔D1-koppeling in de docs.

### D1 — Sportdeelnamemodel (domein)

**69 nodes · 114 edges · 8 sliders · 66 literatuur-bronnen · v2.3.0.**

**Dubbele source-of-truth:**
- *Modelbouw-zijde*: onderzoeks- en ontwerp-ruimte, bevat 8 validatie-
  /transformatie-scripts, 23 analyse-documenten, 10 clusterdefinities,
  4-type curve-bibliotheek, 66 APA7-bronnen, 157 API-cache-entries
  (Crossref/OpenAlex/PubMed).
- *Zeppelin-zijde*: runtime (FastAPI + Jinja2 + HTMX + D3), LLM-guard,
  licentie, UI-sliders, interactieve graph-viewer. Draait op de JSON
  die uit D1-Modelbouw wordt gegenereerd.

D1 gebruikt **het Zeppelin-schema** (STRUCTURAL/MEDIATING/MODERATOR/
FEEDBACK/SOCIAL_REGULATORY, 3 curve-types) — dat is hetzelfde als
Zeppelin v2. **Beide zijden volgen dus niet de A_-protocol-8 maar
Zeppelin-5**; de Modelbouw-README claimt protocol v0.3-compliance,
maar in de data staat Zeppelin-schema.

**Dominante route:** B + C. Route B is live via Zeppelin. Route C (data-
inventarisatie KNSB, E04) is kritiek-pad maar in backlog; blokkeert
E06 scenario-analyse en E07 validatie.

**Secundair:** A (via Zeppelin's `/reasoning`-endpoint, live maar
beperkt). D (literatuur-indexering via E12 backlog).

**Onaf:** E04 data-inventarisatie, N066-orphan-fix (in Zeppelin via
moderator-check-uitzondering werkend, in Modelbouw nog apart),
generalisatie naar andere sporten (E14/E16 nieuwe epics).

### C1 — Capability Model Data-Informed Werken

**Inception.** Geen JSON-graaf nog, wel masterbacklog (16 epics, 85
stories), literatuur-verkenning afgerond (6 data-literacy-raamwerken
vergeleken), documentanalyse-protocol klaar, interview-protocol voor
contextdiagnose klaar.

**Architecturaal herpositioneerd** (maart 2026, D2→C1): niet meer een
domeinmodel maar een **zijwaartse elaboratie** van de L2-capability-node
`data_capability`. Cultuur als stock-node (node_class: stock, role:
modererend, change_rate: slow 3-7 jaar).

**Dominante route:** niet te zeggen — fase te vroeg. Verkennend zijn
A (LLM-context) en D (onderzoeksbasis) logisch in inception; B en C
pas na v1.0-formalisering.

**Onaf:** alles behalve het conceptuele fundament. Nodes/edges nog niet
geformaliseerd, JSON-conversie (E06) in backlog, geen visualisatie.

### A_ — Modulaire Modelarchitectuur (architectuur-laag)

**Protocol v0.3 (29/36 stories done) · 8 edge-types · 4 curve-types ·
node-classes (regular/stock) · evidence A/B/C · capability-rol ·
referentie-implementaties GVM + CSM · `pipeline.py` (630 regels).**

A_ is zelf geen model-in-de-zin-van-inhoud maar een **protocol-en-
tooling-laag**. GVM (Generiek Vermogensmodel meso) is een
generalisatie-kopie van L2. CSM (Causaal Systeemmodel macro) is
generalisatie van L3. Beide zijn blueprints + werkende JSON, niet
gescheiden van de bron-modellen.

**`pipeline.py`** doet een volledige micro→meso→macro doorrekening:
25 WP4-items → dimensiescores → 21 vermogensscores → 6 profielen → 5
uitkomsten → strategische impact. Deterministisch, geen stochastiek.
Werkt op GVM+CSM-data. Draait **niet** op Zeppelin-v2-schema zonder
mapping.

**Dominante route:** dient alle routes. A_ is de grammatica waarin de
routes hun zinnen bouwen.

**Onaf:** `GVM_A2_edges.json` ontbreekt nog (mechanische generatie),
transfer-functies tussen niveaus kwalitatief maar niet wiskundig,
pipeline-gewichten ongevalideerd (theoretisch).

---

## 3. Gedeelde minimale basis

Ondanks de opvallende verschillen hieronder beschreven hebben álle
modellen nu al **vier bindende eigenschappen** gemeen. Dat is
waardevol: het betekent dat harmonisatie niet van nul hoeft te
beginnen — er is een impliciete familie-gelijkenis die formeel
gemaakt kan worden.

### 3.1 Grafstructuur met nodes, edges en sliders

Alle zes modellen (inclusief C1 in conceptuele vorm) zijn gerichte
causale graphs. Nodes representeren *factoren, vermogens of
capabilities*; edges zijn *beïnvloedings-relaties* met een
richting, een sterkte en een vorm; sliders zijn *parameters* die
edges moduleren of (bij L3) de context vastleggen. Die
basisstructuur is stabiel.

Wat per model varieert is hoe rijk de node/edge-metadata is
(L1/L2/L3/D1: rijk, C1: nog niet), maar de shape is gelijk.

### 3.2 Literatuur-onderbouwde edges

Elk model dat voorbij inception is (L1, L2, L3, D1) heeft **edges
aan literatuur-bronnen gekoppeld** (L1: 204, L2: 97, L3: 900, D1: 66).
De koppeling is nog niet cross-model — `L053` in D1 is niet hetzelfde
als `L053` in L1 — maar het *patroon* is identiek: per edge een lijst
met bron-identifiers.

Dit is waarschijnlijk de **beste ingang** voor cross-model-harmonisatie
(zie §5). Het streven dat Max noemde — "literatuur gedeeld en
uniform beheren" — is feitelijk al half klaar: elk model heeft
zijn eigen tabel, een gedeelde tabel met dezelfde schema-velden is
een mechanische samenvoeging als de bron-identificatie consistent
wordt.

### 3.3 Evidence-niveaus A / B / AUDIT (of vergelijkbaar)

L1 heeft dit expliciet (A/B/AUDIT), D1 heeft het in vergelijkbare
vorm (A/B/-), L2 heeft impliciete "gevalideerd / ongevalideerd"-
markering via het validatie-proces, L3 heeft onzekerheidslabels
(low/medium/high) op edges, A_ heeft A/B/C vastgelegd in protocol
v0.3. **Exact dezelfde categorie-scheiding in vorm, verschillende
labels.** Harmonisatie naar één drieletterig schema is laag-
risico en levert meteen cross-model-audits op ("alle AUDIT-edges
in alle modellen" als één query).

### 3.4 Curve-vocabulaire

LINEAR, SATURATING, INVERTED_U, THRESHOLD_LOGISTIC (met enkele
variaties in namen en parameters) komt in alle modellen terug waar
edges wiskundig vormgegeven zijn. L1 heeft alle vier, D1 heeft drie
(LINEAR, INVERTED_U, THRESHOLD_LOGISTIC — `SATURATING` heet daar
zo niet maar komt conceptueel terug), L3 heeft LINEAR +
SATURATING + EXPONENTIAL (en parametriseert kwalitatief). L2 gebruikt
curve-definities op sliders eerder dan op edges.

Harmonisatie-potentie is hier gemiddeld: de *vormen* zijn
overlappend, de *parametrisatie* verschilt soms.

### 3.5 Wat niet bindt

Belangrijk om expliciet te benoemen, want deze punten worden vaak
impliciet gelijk gesteld terwijl ze in de data verschillen:

- **Edge-typologieën** — zie §1 van deze verkenning. Drie
  verschillende systemen in gebruik, ondanks een protocol-claim.
  A_-protocol-8 (enables/threatens/…) is nergens in een
  werkend model geïmplementeerd.
- **Slider-semantiek** — L1 heeft kalibratie-sliders (context van
  een casus), D1 heeft interventie-sliders (beleidsknoppen), L3
  heeft context-parameters (scenario-assen, niet numeriek). Deze
  drie zijn niet inwisselbaar en moeten in elk protocol expliciet
  onderscheiden worden.
- **Node-classes** — A_ v0.3 definieert regular vs stock, C1
  gebruikt stock voor cultuur, L1/L2/D1 hebben geen node_class-
  veld. Eenmalige toevoeging mogelijk, maar betekenisvol voor hoe
  modellen doorrekenen (stocks veranderen traag, reguliere nodes
  kunnen snel).
- **Capability-rol** — alleen C1 en L2 gebruiken dit expliciet.
  Voor L1 zou "vermogen" feitelijk *ook* een capability zijn maar
  de term wordt daar niet gebruikt.

### 3.6 Minimale gemeenschappelijke deler — voorstel-schema

Als we één schema-kern zouden destilleren die **elk model nu al
aankan zonder het inhoudelijk te raken**, dan bevat die:

```
model:
  id: str                          # bv. "L1", "D1"
  version: semver
  literatuur_register_ref: URI     # verwijzing naar gedeelde register

node:
  id: str                          # schema per model (N###, SPORT-UIT-L0-001, …)
  label: str
  definition: str
  domein: str                      # optioneel
  level: str                       # optioneel
  evidence_tier: A | B | AUDIT     # nieuw veld, uniform
  lit_ids: [str]                   # refs in het gedeelde register
  indicators: [str]                # optioneel, voor route C

edge:
  id: str
  source: str
  target: str
  typology:                        # niet één veld maar twee:
    systemic_role: str             # L1-stijl (STRUCTURAL/MEDIATING/…)
    action_verb: str               # A_-stijl (enables/threatens/…)
                                   # laat modellen hun bestaande gebruik behouden
  strength: float
  curve:
    name: LINEAR | SATURATING | INVERTED_U | THRESHOLD_LOGISTIC
    params: dict
  evidence_tier: A | B | AUDIT
  lit_ids: [str]

slider:
  id: str
  semantic_role: kalibratie | interventie | context  # expliciet!
  # rest per-model
```

Dit is de **minimale toevoeging** die elk model ondersteunt zonder
dat iets herschreven hoeft. De grootste interventies zijn:

- `evidence_tier` in uniforme vorm
- `literatuur_register_ref` gedeeld tussen modellen
- `typology.systemic_role` + `typology.action_verb` als twee
  parallelle velden op edges — elk model vult in wat het heeft,
  niemand wordt gedwongen te kiezen voordat het cross-project-
  gesprek er was
- `semantic_role` op sliders — expliciet maakt dat een D1-slider
  niet per ongeluk als L1-slider wordt behandeld

---

## 4. Vier routes uitgewerkt

Per route beschrijf ik: de **use-case** (wie doet wat), de **vereiste
modeleigenschappen**, **per model de haalbaarheid nu** (groen = doet het
al, geel = mist kleine laag, rood = fundamenteel werk nodig), en
**openstaand werk** voor wie deze route zou willen optillen.

### 4.1 Route A — LLM-context met casus + kalibratie

**Use-case.** Gebruiker (docent, coach, adviseur, beleidsmaker)
beschrijft een concrete casus in een gestructureerd capture-formulier,
inclusief kalibratie-sliders. Een LLM krijgt als context het model
(nodes + edges + curves + evidence) plus de casus en redeneert naar
een analyse met hypotheses en aanbevelingen die het respons-template
invullen.

**Vereiste modeleigenschappen.**
- Nodes en edges moeten **leesbaar zijn voor het LLM**: definitie,
  rol, mechanisme per edge, niet alleen ID's. L1's uitwerking
  (~4500 woorden per node) is de gouden standaard; compacter kan
  ook maar de inhoud moet aanwezig zijn.
- Een **capture-template** (casus-input) dat de LLM-prompt
  structureert — welke context-velden, welke sliders.
- Een **respons-template** (analyse-output) zodat het LLM weet waar
  naartoe te werken en de kwaliteit vergelijkbaar blijft tussen
  sessies.
- **Kalibratie-sliders** (geen interventie-sliders): ze beschrijven
  de casus, ze veranderen niet het beleid.
- Een **system-prompt** die het model, het capture-formulier en het
  respons-template in één LLM-call combineert.

**Haalbaarheid per model.**

| Model | Stand | Toelichting |
|---|---|---|
| L1 | 🟡 | Capture-canvas + respons-template bestaan en zijn af; system-prompt ontbreekt; kalibratie-sliders zijn de bestaande 4. Nog ontbreekt: een applicatie (CLI, webapp of notebook) die het samen als prompt-chain aan een LLM aanbiedt. |
| L2 | 🟢 | Diagnose-pipeline (vragenlijst → scoring → profielmatching) is effectief al een sterkere vorm van route A — alleen verloopt de "redenering" deterministisch in plaats van via LLM. LLM zou de output kunnen omzetten in natuurlijke-taal-verhaal of een verdiepend gesprek aangaan. |
| L3 | 🟡 | Beleidsplan-doc (52 p.) + gespreksleidraad (8 p.) functioneren als pre-gemaakte analyse-output. Een LLM zou per-gesprek een custom analyse kunnen maken in plaats van één gefixeerd rapport. Vereist vertaling van de 5 scenario-assen naar een LLM-invoerbaar formaat. |
| D1 | 🟡 | Zeppelin's `/reasoning`-endpoint doet dit al beperkt (LLM krijgt v2-model als context, gebruiker stelt een vraag). Maar er is geen expliciet capture-template met casus-structuur; het is meer één-shot-Q&A. |
| C1 | 🔴 | Inception, geen model-data. Route A theoretisch mogelijk zodra E04/E05/E06 (nodes, edges, JSON) af zijn. |

**Openstaand werk.**
- **Voor L1 specifiek**: een **runner-script of notebook** schrijven
  dat capture-canvas + VM_A1/A2/A3-JSON + respons-template tot één
  LLM-prompt combineert. Small — schatbare omvang van een paar dagen.
  Dat levert onmiddellijk een werkend route-A-prototype voor L1 op
  zonder de modellen aan te raken.
- **Cross-model**: een **gedeelde prompt-bibliotheek** (capture-templates
  + respons-templates) die per model in dezelfde *shape* zit. Dat
  kan een `prompts/`-map zijn in elke modelfolder, met dezelfde
  bestandsnamen.

### 4.2 Route B — Interactieve app

**Use-case.** Gebruiker manipuleert sliders als beleids-interventies,
ziet in real-time wat dat voor node-waarden betekent via
voortpropagatie door de graaf. Kernfunctie van Zeppelin voor D1.

**Vereiste modeleigenschappen.**
- **Interventie-sliders** met expliciete curve-types en
  sensitiviteiten per edge.
- Een **propagatie-engine** die slider-waarde-verandering naar node-
  verandering rekent (Zeppelin's `dag_engine.py`, Modelbouw's
  `pipeline.py`).
- Een **visualisatie-laag** (D3, Gephi, Cytoscape) die de graaf
  toont met interactieve elementen.
- **Snelle feedback**: de voortpropagatie moet real-time genoeg zijn
  voor een natuurlijke slider-interactie.

**Haalbaarheid per model.**

| Model | Stand | Toelichting |
|---|---|---|
| D1 | 🟢 | Zeppelin is live. Slider-interactie, voortpropagatie, D3-viz, LLM-guard, licentie, auth allemaal operationeel. |
| L2 | 🟡 | GEXF beschikbaar voor Gephi (lees-only). Interactieve app (E07) in backlog maar PRD-fase. Diagnose-pipeline zou via een web-UI goed werken. |
| L1 | 🟡 | GEXF export werkt, PRD voor "Vermogensmodel Explorer" geschreven (`app/` folder met docs). Code niet gestart. Zou kunnen meeliften op Zeppelin-architectuur. |
| L3 | 🟡 | Gespreksleidraad + scenario-doorwandelings-scripts werken offline. Interactieve scenario-app (S05-03) geparkeerd omdat Max eigen app bouwt — potentieel dubbel werk. |
| A_ | 🟢 | `pipeline.py` doet de rekenkant voor GVM+CSM. Zou als runtime-engine onder een app kunnen zitten (vergelijkbaar met Zeppelin's dag_engine). |
| C1 | 🔴 | Geen data. |

**Openstaand werk.**
- **Strategische keuze**: één gedeelde app-runtime of meerdere?
  Zeppelin is D1-specifiek opgebouwd. Het zou **onevenredig veel
  werk zijn** om Zeppelin multi-model te maken (schema verschilt,
  sliders-semantiek verschilt, UI-aannames verschillen). Een
  pragmatische route is: **per model een lichte app-laag die
  hetzelfde protocol (schema) implementeert**, niet één monolithische
  app.
- **Voor L1/L2**: als een interactieve app wél gewenst is, kan men
  de Zeppelin-stack (FastAPI + Jinja2 + HTMX + D3) als *template*
  gebruiken zonder dezelfde repo te zijn. Dat geeft
  consistentie-voordeel zonder technische koppeling.

### 4.3 Route C — Koppeling aan echte data

**Use-case.** Node-waarden komen (deels) uit databronnen: vragenlijsten,
ledensystemen, jaarverslagen, KPI-dashboards. Het model wordt
"gevoed" — niet alleen handmatig ingevuld. Kwantitatief of
kwalitatief.

**Vereiste modeleigenschappen.**
- **Indicator-slots op nodes**: per node een of meer verwijzingen
  naar meetbare waarden (Likert-item, CBS-reeks, interne KPI). Nu
  het grootste gat in alle modellen.
- **Transformatie-laag**: hoe komt een indicator-waarde (bv. Likert
  1-5 of een percentage) tot een node-waarde in het model (vaak
  [0, 1])?
- **Versionering van data-snapshots**: elke meting is een
  tijdstempel; het model krijgt meerdere "fotomomenten".
- **Onzekerheids-propagatie**: Likert-gemiddelden hebben een
  spreiding, KPI's hebben ruis — dat zou meegerekend moeten worden,
  niet weggepunt tot één getal.

**Haalbaarheid per model.**

| Model | Stand | Toelichting |
|---|---|---|
| L2 | 🟡 | Vragenlijst (78 items) bestaat en is gevalideerd tegen 6 profielen. Mapping item→node impliciet in E1-E2-schema; expliciet `indicator`-veld op nodes ontbreekt. Koppeling met Vitaliteitsindex/NOC*NSF genoemd maar niet uitgewerkt. Snelste weg naar route C. |
| L3 | 🟡 | C1/C2/C3-classificatie-raamwerk voor documenten werkt, eerste snapshot gevuld. Voor kwantitatieve indicatoren (KPI's → node-waarden) is nog geen infrastructuur. |
| D1 | 🔴 | Data-inventarisatie KNSB (E04) kritiek-pad maar in backlog. Kandidaat-nodes benoemd (N015 Licentiekosten, N016 Accommodatie, N039 Wedstrijdaanbod, N044 Bestuurlijke prioriteiten) maar geen indicator-laag. |
| L1 | 🔴 | Weinig relevant — vermogens zijn niet direct meetbaar uit bestaande systemen. Leerlingvolgsysteem als theoretische optie genoemd. |
| C1 | 🔴 | Geen model. E09 (contextdiagnose NOC*NSF) is geplande eerste data-koppeling. |

**Openstaand werk.**
- **Indicator-schema uitwerken**: wat betekent het dat een node
  "gekoppeld is aan" een indicator? Voorstellen:
  `node.indicators = [ {source_id, transform, confidence} ]` — een
  lijst (meerdere indicatoren per node mag), een source-ID (bv.
  `NSkiV_LEDEN_2026Q1.actief_jeugd`), een transformatie (hoe komt
  de waarde naar [0,1]?), en een vertrouwensgraad.
- **Starten met L2**: L2's vragenlijst is de meest volwassen data-
  laag en de conversie is deterministisch — daar kan men het
  indicator-schema het scherpst testen en verfijnen vóór D1 en L3
  erop aansluiten.
- **D1-specifiek**: E04 data-inventarisatie KNSB prioriteren. Dit
  staat in de Modelbouw-backlog maar is blokkerend voor scenario-
  analyse en validatie.

### 4.4 Route D — Onderzoeks-archief en reproduceerbaarheid

**Use-case.** Het model als wetenschappelijk artefact. Iemand wil
over 5 jaar kunnen nagaan: welke literatuur ondersteunde deze edge?
Welke versie van het model is gebruikt in publicatie X? Kan iemand
de analyse reproduceren?

**Vereiste modeleigenschappen.**
- **Semantische versionering** (semver of vergelijkbaar).
- **Git-geschiedenis** voor code en data.
- **Cross-model literatuur-register** met stabiele identifiers
  (DOI's waar mogelijk).
- **Citeerbare bestandsverwijzingen** (liefst DOI's voor de modellen
  zelf via Zenodo of vergelijkbaar).
- **Changelog per model**: wat veranderde tussen v1.0 en v1.1?
- **Reproduceerbaarheid-test**: draait de oude versie nog?

**Haalbaarheid per model.**

| Model | Stand | Toelichting |
|---|---|---|
| L1 | 🟢 | 204 bronnen, systematische methodologie-documenten, interventie-synthese. Mist alleen de cross-model register-uitlijning. |
| L3 | 🟢 | 900 bronnen, thema-rapporten T01-T14, checkpoint-rapporten per wave, uitgebreide output-documentatie. **Geen git** is het grootste gat (S01-02 open). |
| L2 | 🟡 | 97 bronnen, methodologische verantwoording, 6 citatie-issues geaccepteerd. **Bewust geen git** tot v1.1; Obsidian als versiebeheer. |
| D1 | 🟡 | 66 bronnen, API-cache (Crossref/OpenAlex/PubMed), E12 literatuur-pipeline in backlog. Semver-ondersteund (v2.3.0). Zeppelin-zijde heeft git + CI. |
| C1 | 🔴 | Literatuuranalyse gedaan (12 frameworks vergeleken) maar nog geen eigen bronnen-lijst. |
| A_ | 🟢 | Protocol v0.3 gedocumenteerd, documentatie-standaard v1.1, epic-historie traceerbaar. |

**Openstaand werk.**
- **Cross-model literatuur-register** als eerste bouwsteen (zie §5
  voor de aanpak).
- **Git voor L2 en L3** — L2 bewust uitgesteld tot v1.1, L3
  staat in S01-02 als open story. Lage drempel om te doen.
- **Zenodo-DOI per model-versie** bij v1.0-release zodat het model
  een stabiele citeerbare referentie krijgt.

---

## 5. Harmonisatie-voorstellen

Gesorteerd van laag-hangend-fruit (veel winst, weinig risico) naar
architecturaal-ingrijpend (veel winst, veel risico). Elk voorstel met
*scope*, *aanname*, *risico*, en *gevolg voor bestaande modellen*.

### 5.1 Laag-hangend — cross-model literatuur-register

**Scope.** Eén gedeelde tabel met bibliografische bronnen, stabiele
identifiers (bij voorkeur DOI's), en een convertie-tabel naar de
huidige per-model-IDs (`L053` in D1, `lit_id_147` in L3, etc.).

**Aanname.** Elk model houdt zijn eigen `lit_ids`-veld, maar de
waardes daarvan worden (waar mogelijk) genormaliseerd tot gedeelde
identifiers. Waar de bron al een DOI heeft: gebruik die. Waar niet:
een stabiele MB-register-ID (`MB-REG-00123`).

**Risico.** Minimaal. Geen inhoudelijke wijziging aan modellen. Werk
is administratief: de 204+97+900+66 ≈ 1267 bronnen samenvoegen,
duplicaten detecteren (verwacht 20-40%), één hoofdtabel opbouwen.

**Gevolg voor bestaande modellen.** Zero-breakage. Per-model een
`lit_mapping.json` die oude IDs naar gedeelde IDs vertaalt; modellen
kunnen oude IDs blijven gebruiken tot ze bij eerstvolgende grote
refresh migreren.

**Waarom dit als eerste.** Het is pure winst voor route D, het is de
enige integratie waar Max expliciet voorkeur voor uitsprak ("op
termijn streven"), en het levert onmiddellijk een cross-model-
evidence-query op ("welke edges in L1, L2, D1 en L3 delen dezelfde
bron?").

### 5.2 Laag-hangend — uniforme evidence-tiers

**Scope.** Elk model normaliseert zijn evidence-label naar `A | B |
AUDIT` (of gelijkwaardig drieletterig schema). Op nodes én edges.

**Aanname.** De bestaande semantiek is al compatibel — L1 heeft
expliciet A/B/AUDIT, D1 heeft A/B/-, L3 heeft low/medium/high, L2
impliciet gevalideerd-vs-niet. Dit is een **label-wijziging**, geen
inhoudelijke herbeoordeling.

**Risico.** Laag. Per model is er een eenmalige vertaaltabel nodig
(bv. L3 low→AUDIT, medium→B, high→A). Voorzichtigheid: de tabellen
moeten door een inhoudelijk-betrokkene beoordeeld worden, niet
automatisch — want "low" kan in context iets anders betekenen dan
"AUDIT".

**Gevolg voor bestaande modellen.** Eenmalige label-update via script.
Niet-brekend voor consumers die op de tekst-labels matchen zolang
de mapping conservatief is.

**Waarom nuttig.** Cross-model-audits ("welke AUDIT-edges bestaan er,
over alle modellen heen?") worden mogelijk. Evidence-rapportage in
LLM-route A kan één woordenschat gebruiken.

### 5.3 Middel — gedeelde protocol-herziening v0.4

**Scope.** De bestaande `gedeeld_protocol.md` v0.3 wordt bijgewerkt
omdat de claim "alle modellen volgen dit protocol" in de data niet
klopt. v0.4 erkent **twee parallelle edge-typologieën**:

1. `systemic_role` — structurele rol in het systeem (STRUCTURAL,
   MEDIATING, MODERATING, FEEDBACK, SOCIAL_REGULATORY). L1, L2, D1
   gebruiken dit. Antwoord op "wat doet deze edge in het systeem?"
2. `action_verb` — actiewerkwoord voor de beïnvloeding (enables,
   threatens, requires, modulates, competes_with, improves, shapes,
   erodes). L3 gebruikt grotendeels dit (met variaties). Antwoord
   op "wat doet deze edge inhoudelijk?"

**Aanname.** Beide typologieën zijn geldig en inhoudelijk
complementair, niet vervangend. Een edge **kan** beide velden hebben,
**moet** er één hebben.

**Risico.** Middel. Het vraagt een bewuste herpositionering van het
protocol ("we erkennen dat er twee assen zijn, niet één"). Als men
hierin niet mee wil gaan is het alternatief: **één van de twee tot
norm verklaren en de andere migreren** — maar dat betekent
L1/L2/D1 óf L3 moet een typologische migratie doen, wat inhoudelijk
werk is.

**Gevolg voor bestaande modellen.** Geen migratie nodig zolang
modellen binnen hun eigen typologie blijven. Een tweede veld kan
per model optioneel worden toegevoegd wanneer de auteurs daar
zinvolle uitspraken over kunnen doen. **Expliciet geen eenzijdige
migratie.**

### 5.4 Middel — slider-semantiek expliciet maken

**Scope.** Elk model krijgt op zijn sliders een `semantic_role`-veld
met drie toegestane waarden:

- `kalibratie` — de slider beschrijft de context van een casus
  (L1-stijl). Verandert niet tijdens een analyse-sessie.
- `interventie` — de slider is een beleidsknop (D1/L2-stijl). Wordt
  verschoven om wat-als te zien.
- `context` — de slider beschrijft externe omstandigheden (L3-stijl:
  klimaat, economie). Meestal kwalitatief en scenario-gebonden.

**Aanname.** Een slider heeft **één** semantische rol; hybriden
worden vermeden door de ambiguïteit expliciet te maken en de auteur
tot een keuze te dwingen.

**Risico.** Laag. Klassificatie-oefening, geen code-wijziging.

**Gevolg voor bestaande modellen.** Eenmalige toevoeging van een
veld op elke slider. Consumers (Zeppelin, LLM-prompts, pipeline.py)
kunnen vanaf v0.4 **verschillend reageren op verschillende slider-
typen** — bijvoorbeeld: interventie-sliders krijgen een
simulatie-knop, kalibratie-sliders een "leg de casus vast"-knop.

### 5.5 Middel — node-class en capability-rol bij volgende revisie

**Scope.** Bij elke eerstvolgende grote revisie van L1/L2/D1: voeg
`node_class: regular | stock` toe, en (waar van toepassing)
`role: capability` om zijwaartse elaboraties mogelijk te maken.

**Aanname.** C1 en A_ hebben dit al uitgedacht; L1/L2/D1 hebben het
impliciet (bv. D1's `Mediaprofilering` gedraagt zich als een stock
— veranderingen duren jaren — maar wordt niet als zodanig
gelabeld).

**Risico.** Middel. Per-node moet een inhoudelijke keuze gemaakt
worden. De meeste nodes zijn `regular`, minderheid is `stock`.
Makkelijke heuristiek: veranderingen van dit concept duren meer
dan 1 jaar? Dan stock.

**Gevolg voor bestaande modellen.** Toegevoegd veld met default
`regular` — geen migratie nodig voor consumers, maar wel voor de
propagatie-engine als die tijd-schalen gaat gebruiken. Zeppelin's
`dag_engine.py` propageert nu instant; voor stock-nodes zou een
traagheids-factor zinvol zijn (dat is grotendeels Pad A voor
`time_lag` uit de Zeppelin-roadmap).

### 5.6 Ingrijpend — gedeelde node/edge-Pydantic-basis

**Scope.** Eén Pydantic-module (bv. `modelbouw_core/`) met het
minimale gedeelde schema uit §3.6, geïmporteerd door alle modellen
die Python-tooling hebben (Zeppelin voor D1, `pipeline.py` voor A_,
toekomstige apps voor L1/L2).

**Aanname.** Modellen die geen Python-tooling hebben (L3 werkt
grotendeels met JSON+scripts) kunnen een schema-validator-script
gebruiken zonder de Python-module zelf te importeren.

**Risico.** Hoog. Dit creëert **één technische afhankelijkheid**
tussen modellen die nu ontkoppeld zijn. Als er een bug in het
schema zit, breken meerdere modellen tegelijk. Omgekeerd: één
verbetering (bv. een validator) werkt overal. Voor of tegen is een
architecturale keuze die over jaren geldt.

**Gevolg voor bestaande modellen.** Zeppelin's `app/core/graph_models.py`
zou opgaan in `modelbouw_core.Graph`. Dat raakt het werk dat we in
S14-02 net hebben neergezet. Niet nu doen, maar wel in de gaten
houden: als dit over 6-12 maanden gewenst is, is de S14-02-laag
precies het startpunt.

**Aanbeveling.** Niet nu. Eerst 5.1-5.5 (de niet-ingrijpende
voorstellen) doorlopen en zien of de gedeelde basis in de *data*
staat, voordat er een gedeelde basis in *code* ontstaat.

### 5.7 Ingrijpend — unificatie van pipelines en apps

**Scope.** Eén runtime-engine voor alle modellen: Zeppelin's
`dag_engine.py`, Modelbouw's `pipeline.py` en een eventuele L2-
simulatietool smelten samen.

**Risico.** Zeer hoog. Zeppelin is D1-geoptimaliseerd; pipeline.py
is multi-level-geoptimaliseerd; een L2-tool zou andere eisen
stellen (vragenlijst + matching). Generalisatie kost maanden en
heeft ongewis inhoudelijk gewin.

**Gevolg voor bestaande modellen.** Potentieel groot. Ook potentieel
verlammend (ze moeten allemaal wachten tot de unified engine af is).

**Aanbeveling.** **Niet doen tenzij er een concrete product-aanleiding
is.** Dit is het soort integratie dat op papier elegant oogt maar in
de praktijk een rem op elk individueel model wordt. Uitzondering: als
uiteindelijk een consument (bv. NOC*NSF) wil dat L1→L2→L3→D1 binnen
één sessie doorgerekend wordt, dan is dit verdedigbaar. Tot dan is
het vermijden van deze stap verstandig.

---

## 6. Openstaande beslissingen + aanbevolen volgorde

### 6.1 Beslissingen waar Max later een keuze over moet maken

Dit zijn keuzes waarvan de inhoudelijke richting nu niet vast hoeft
te liggen, maar die op termijn terug zullen komen. Ze zijn hier
benoemd zodat ze niet impliciet worden gemaakt.

1. **Twee-assen-typologie vs één-typologie.**
   Volgt men 5.3 (twee velden — structural_role + action_verb)
   of dwingt men alsnog convergentie naar één norm? Voor-voor:
   respecteert bestaande modellen. Voor-tegen: twee velden kan
   voelen als weifelen. Besluit zinvol ná een concrete cross-model-
   vraag waar de typologie-ambiguïteit in de weg zat.

2. **Eén-app of meerdere-apps voor route B.**
   Zeppelin multi-model maken of elk model z'n eigen lichte app
   geven? Nu is Zeppelin D1-specifiek; de eerste optie is
   architecturaal zwaar, de tweede vraagt dat elk model-team-lid
   zelf codeert. Beslissing hangt af van wie de apps uiteindelijk
   onderhoudt en wie ze gebruikt.

3. **Of Zeppelin de code-koepel wordt voor alle modellen** (zie
   5.6). Nu doet Zeppelin alleen D1-runtime. Als de gedeelde
   Pydantic-basis later wordt gebouwd, is Zeppelin's `app/core/` de
   logische plek. Maar dat creëert een technisch monopoly dat
   bewust gekozen moet worden.

4. **Waar de Modelbouw-map thuishoort.** Nu is het een losse folder.
   Voor sommige routes (C data-koppeling, D onderzoeks-archief)
   wint het aan versioning + CI als het een git-repo wordt. Dat
   is een governance-vraag: één mega-repo, repo-per-model, of
   iets ertussen (bv. monorepo met submappen).

5. **Cross-project-documentatie-eigenaarschap.** De
   `meta-architectuur.md`, `PROJECTSTATUS_Modelbouw.md`,
   `documentatiestandaard.md` zijn nu centraal. Als de modellen
   uit elkaar gaan groeien (eigen repo's, eigen owners), wie houdt
   die doorlopend actueel? Voor nu één persoon (Max); als het
   team groeit is dit een rolkeuze.

### 6.2 Beslissingen die beter expliciet gemaakt worden

Deze zijn impliciet al gemaakt en zouden gedocumenteerd moeten
worden zodat ze niet onbedoeld heroverwogen worden:

- **L1 is de brontekst van protocol v0.3, maar L1 volgt v0.3 zelf
  niet in zijn edge-typologie.** Dit is feitelijk inconsistent in
  de docs. Of v0.3 op L1 wordt aangepast, of L1 op v0.3, of beide
  blijven zoals ze zijn met een toelichting — maar de huidige
  tegenstrijdigheid in de meta-architectuur zou opgehelderd
  moeten worden.
- **C1 is *geen* domeinmodel.** De D2→C1-herpositionering is goed
  vastgelegd in EPICS_C1.md maar de naamgeving "Capability Model"
  is voor buitenstaanders nog ambigu. Expliciete term: C1 is een
  *elaboratie-model* van één L2-node.
- **Zeppelin is geen onderdeel van Modelbouw.** De repo staat
  elders (graaf_zeppelin). D1 heeft daardoor een feitelijke
  dubbele source-of-truth. Dat hoeft geen probleem te zijn, maar
  de rolverdeling (Modelbouw-D1 = onderzoek, Zeppelin-D1 =
  runtime) zou ergens expliciet vastgelegd moeten worden.

### 6.3 Aanbevolen volgorde

Niet als route-met-deadlines, wel als **volgorde van redeneringen**:
eerst wat nu betaalbaar en winst oplevert, dan wat structureel werk
vraagt, dan wat strategische commitment vraagt.

**Korte termijn — 2-4 weken werk, weinig risico:**

1. **Literatuur-register samenvoegen** (5.1). Eén tabel, DOI's waar
   mogelijk. Per-model `lit_mapping.json` zodat bestaande refs
   blijven werken. Fungeert als ankerstuk voor cross-model-
   evidence-audits.
2. **Uniforme evidence-tiers** (5.2). Label-vertaling per model.
3. **Slider-semantiek expliciet** (5.4). Één veld op elke slider.
4. **Git voor L2 en L3** (open punten uit hun projectstatus). Laag-
   hangend, consequentie is dat versie-tracking tot een standaard
   wordt.
5. **L1 route-A-prototype** (§4.1 openstaand werk). Notebook of
   script dat capture-canvas + VM-JSON + respons-template tot één
   LLM-call combineert. Bewijst dat het patroon werkt zonder
   commitment op een app.

**Middellange termijn — afhankelijk van waar Max prioriteit legt:**

6. **Protocol v0.4** (5.3) *als* na stap 1-5 blijkt dat de twee-
   assen-typologie onmisbaar is. Uitstellen als het nog niet knelt.
7. **Node-class + capability-rol** (5.5) bij eerstvolgende grote
   revisie per model. Niet als aparte oefening.
8. **Indicator-schema op nodes** (§4.3 openstaand werk) — beginnen
   bij L2 waar de vragenlijst al bestaat. Uitbreiden naar D1 (E04)
   en L3 (kwartaal-KPI's) als dat daar nuttig is.
9. **D1 E04 data-inventarisatie KNSB** — geparkeerd maar kritiek-
   pad voor Zeppelin-meerwaarde.

**Lange termijn — strategische commitment vereist:**

10. **Gedeelde Pydantic-basis** (5.6) wanneer de data-harmonisatie
    zich uitkristalliseert. Niet preventief.
11. **Unified runtime** (5.7) alleen bij een concrete product-
    aanleiding.
12. **Eventuele overname door NOC*NSF of andere organisatie** —
    governance-keuze die buiten deze verkenning valt.

### 6.4 Risico's bij inaction

Expliciet benoemd omdat niet-doen ook een keuze is:

- **Literatuur drift.** Hoe langer 4 losse bronnen-tabellen blijven,
  hoe groter de kans dat dezelfde bron onder 2-3 verschillende IDs
  komt. Over 3 jaar is dit een stuk vervelender op te ruimen.
- **Zeppelin-vs-Modelbouw-schisma voor D1.** Als de ontwerpruimte
  (Modelbouw) en runtime (Zeppelin) uit elkaar drijven in schema,
  krijg je conversie-frictie bij elke D1-update. Nu is dat nog in
  orde; hou de vinger aan de pols.
- **C1-inertie.** Inception-fase is vruchtbaar maar kan zichzelf
  verlengen. Enig advies: stel een concreet doel (v0.1-node-lijst,
  zelfs 10 nodes) met een datum.
- **L1 niet in toepassing.** Het model is het rijkst onderbouwd en
  het minst toegepast. Als de LLM-route-A-prototype er niet komt,
  blijft de meeste waarde opgesloten in documentatie.

---

## 7. Afsluiting

Dit document is **niet** een plan — het is een kaart. De routes,
voorstellen en volgordes zijn niet bindend; ze zijn geschreven zodat
je ze kunt afwijzen, reorganiseren of combineren met betere kennis
van de praktijk die ik als buitenstaander niet heb.

Wat ik wél aanraad als fundament onder elke volgende keuze: **de
modellen zijn de magie**. Elke integratiestap die de modellen respectteert
(veld-toevoeging, label-vertaling, gedeelde register) weegt lichter
dan een stap die ze platslaat (één typologie afdwingen, één schema
voorschrijven). Als een stap inhoudelijk werk van de model-auteurs
vraagt, is dat een signaal om hem uit te stellen tot er een concrete
aanleiding is.

De meest concrete eerste win is waarschijnlijk het **literatuur-register
** (5.1). Het is administratief werk, geen nieuw inzicht vereist,
maar de opbrengst is direct zichtbaar en het bouwt vertrouwen op voor
grotere stappen.

---

**Vervolg:**
- Verkenning bespreken, keuzes maken of herformuleren.
- Eventueel dit document naar Zeppelin's `docs/` of naar de Modelbouw-
  map kopiëren en van daaruit per stap een story maken.
- Of parkeren en eerst een concrete product-aanleiding afwachten.
