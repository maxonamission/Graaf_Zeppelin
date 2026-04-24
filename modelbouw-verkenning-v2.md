# Verkenning — Modellen-ecosysteem Modelbouw (v2)

**Status:** Tweede concept, integraal herschreven na eerste bespreking.
**Doel:** De routes en samenhangen tussen zes causale netwerkmodellen
(L1, L2, L3, D1, C1 en de A_-architectuurlaag) zó in beeld brengen dat
Max per onderdeel kan beoordelen wat hij wil doorpakken, zonder dat de
bestaande modellen eraan opgeofferd worden.

**Leeswijzer.** §1 en §2 bouwen het frame en leggen vast wat er al
architecturaal is uitgedacht (dat is aanzienlijk meer dan een
buitenstaander eerst denkt). §3 geeft per model een compact snapshot
tegen die basis. §4 behandelt cross-level relaties als eigen thema,
omdat dat de rode draad van Max' nuances was. §5-6 beschrijven wat de
modellen bindt en hoe sliders over niveaus heen samenhangen. §7 vertaalt
dat naar vier concrete use-case-routes. §8 geeft harmonisatie-
voorstellen, gesorteerd van laag-hangend naar ingrijpend. §9 sluit af
met beslismomenten en volgorde.

---

## §1 Kader

### 1.1 De modellen zijn de magie

De modellen in Modelbouw zijn niet de applicatie; ze zijn het
inhoudelijke werk dat **elke consumer** — een LLM die over een casus
redeneert, een webapp die sliders laat schuiven, een databron-koppeling,
een onderzoekspublicatie — betekenisvol maakt. Dat bepaalt hoe je over
integratie nadenkt: niet "hoe plak ik ze aan elkaar vast", maar "hoe
zorg ik dat elk model naar de use-case waar het voor bedoeld is goed
ontsloten wordt, zonder dat ik de modellen zelf kapot maak".

Dat principe — *respecteren wat er staat* — wordt in dit document
consequent gehanteerd. Waar een voorstel inhoudelijk werk van de
model-auteurs vraagt, wordt dat expliciet benoemd en gekoppeld aan een
concrete aanleiding in plaats van aan een architectuurwens.

### 1.2 Ontwerp-principes (door Max geformuleerd)

Vier principes volgen uit het gesprek en worden verder consistent
gevolgd:

1. **Protocol is werk-in-uitvoering, geen norm.** Het gedeeld protocol
   v0.3 en de architectuurnotities zijn **tussenresultaten van een
   zoektocht**, geen vastgestelde regels die elk model had moeten
   volgen. Claims van de vorm "alle modellen volgen dit protocol"
   overdrijven de status van die documenten.
2. **Niveau-autonomie.** Elk niveau bepaalt zélf welke informatie uit
   andere niveaus het nodig heeft. L2 moet zelfstandig kunnen
   functioneren zonder dat L3-keuzes bekend zijn. De cross-level
   relatie is daarmee een **bottom-up gevraagde context**, niet een
   top-down gedirigeerd gegeven.
3. **Typologie past bij context, samenhang zonder uniformiteit.** Edge-
   typologie mag verschillen per type model (DAG, causaal), niveau
   (micro/meso/macro) en domein. De eis is niet uniformiteit maar
   *samenhang* — dat concepten op verschillende niveaus op elkaar
   aansluiten zonder identiek te zijn.
4. **Uniformiteit waar het representatie betreft, niet waar het
   semantiek betreft.** De *vormen* van edges (LINEAR, THRESHOLD,
   INVERTED_U, SATURATING) en de notatie van hun parameters kunnen
   cross-model identiek zijn. De *betekenis* van edge-types hoort per
   model context-gebonden te zijn.

### 1.3 Vier use-case-routes

Onveranderd sinds de eerste verkenning, maar nu met meer ruimte voor
hoe elk model er anders mee omgaat:

- **Route A — LLM-context met casus + kalibratie-sliders.** Gebruiker
  beschrijft een concrete situatie in een capture-canvas; LLM redeneert
  langs nodes en edges naar een gestructureerde analyse.
- **Route B — Interactieve app.** Sliders als beleids-interventies,
  realtime voortpropagatie, visuele feedback.
- **Route C — Koppeling aan echte data.** Nodes krijgen indicator-
  ankers (vragenlijsten, KPI's, kwalitatieve signalen); het model wordt
  periodiek gevoed.
- **Route D — Onderzoeks-archief.** Het model als citeerbaar,
  versioneerbaar, literatuur-verankerd artefact.

Deze routes zijn niet exclusief: één model kan er meerdere tegelijk
ondersteunen, op verschillende momenten, voor verschillende
doelgroepen.

### 1.4 Wat dit document niet doet

- Geen architectuur-voorschrift. Het document laat ruimte.
- Geen niveau-A/B/C-keuze opleggen; die bleek bij de eerste verkenning
  te vroeg gevraagd.
- Geen prioritering van modellen onderling — prioritering past bij een
  route-uitvoering, niet bij het bestaansrecht.

---

## §2 De architecturale basis die al bestaat

Een belangrijk inzicht bij het lezen van de Modelbouw-folder: de
architectuur voor cross-level samenhang is **grotendeels al
uitgedacht**, alleen niet overal geëffectueerd in de model-data zelf.
Drie documenten dragen die basis:

### 2.1 Stock-nodes + cross-level principe

`A_/docs/architectuurnotitie_stock_nodes_sliders_cultuur.md` v0.2
(maart 2026) formaliseert:

- **Het onderscheid slider vs. stock-node.** Sliders zijn *externe*
  modulatoren (omgevingscondities, door gebruiker ingesteld). Stocks
  zijn *interne* toestandsvariabelen — nodes in de graph die zichzelf
  opbouwen via causale accumulatie en langzaam veranderen.
- **Het cross-level principe:**
  > "Een stock node op niveau N wordt slider op niveau N-1 — voor
  > zover relevant als context voor de vragen die het model op niveau
  > N-1 moet beantwoorden."
  
  Dit dekt Max' punt over niveau-autonomie: de lijst van kandidaat-
  sliders is afgeleid van de stocks op het niveau erboven, maar welke
  je activeert bepaalt het lagere niveau zelf.
- **Nieuwe node-attributen:** `node_class` (regular | stock) en
  `change_rate` (slow | medium | fast) voor stock-nodes. Het
  `erodes`-edgetype om de asymmetrie van stocks (snel afbraak vs.
  trage opbouw) te modelleren.
- **Een indicatieve hertypering van bestaande sliders:** de
  collectieve psychologische veiligheid en prestatiecultuur in GVM
  zijn feitelijk stocks (intern opgebouwd), geen sliders.

Status: **voorstel v0.2**, "ter sturing van L2-modelontwikkeling en
MLS-protocolrevisie". Niet geïmplementeerd in de model-data.

### 2.2 Gelaagd slider-inventaris

`A_/docs/E05_S03_slider_inventaris.md` inventariseert alle 17
sliders over drie niveaus (4 micro + 8 meso + 5 macro) en legt vast:

- **Doorwerkingsketens.** Voorbeeld: SA2 (economisch klimaat) → GS01
  (collectieve werkdruk) → A16 (individuele werkdruk). Met
  **vertraging**: macro→meso in kwartalen, meso→micro in weken-
  maanden.
- **Bandbreedte-principe.** Macro-sliders bepalen niet de waarde van
  meso-sliders maar de *range* waarin ze bewegen: "economisch klimaat
  krap" betekent dat GS01 (werkdruk) niet onder ~0.5 kan.
- **Asymmetrie.** Neerwaartse druk (macro → micro) is sterker dan
  opwaartse invloed (micro → macro). Eén veerkrachtig individu
  verandert de organisatie niet; organisatiebeleid verandert wél de
  werkdruk van alle medewerkers.
- **Uniekheid per niveau.** Sommige sliders bestaan alleen op één
  niveau omdat ze daar pas zinvol zijn (diversiteit, organisatie-
  identificatie op meso; digitale versnelling, economisch klimaat op
  macro).

Status: **uitgewerkt raamwerk**, in L3 operationeel, in L1/L2 deels
overgenomen, in D1 nog niet verbonden met deze taxonomie.

### 2.3 Consistent curve-vocabulaire

Over de modellen heen keren dezelfde curve-vormen terug met
opmerkelijk consistente parameter-notatie:

| Curve | Parameters | Betekenis |
|---|---|---|
| LINEAR | — | Rechtlijnig |
| THRESHOLD_LOGISTIC | `t` (drempel), `k` of `a` (steilheid) | Sigmoïde rond drempel |
| INVERTED_U | `μ` (optimum), `σ` (breedte) | Gaussisch optimum |
| SATURATING | `k` (verzadigingsconstante) | Verzadiging |

Alle vier komen voor in L1, een deel in L2/L3/D1, in hoofdletters en met
Griekse letters waar de literatuur dat doet. Dit is *de facto* uniform —
niet omdat een protocol het afdwingt, maar omdat de onderliggende
wiskundige vormen beperkt zijn en de modelbouwers consequent geweest
zijn.

### 2.4 Wat dit betekent voor het advies

Omdat de architecturale basis al uitgedacht is, schuift de vraag van
"wat zou de architectuur moeten zijn?" naar "welke delen van de
bestaande basis zijn doorgetrokken in de data en welke niet — en wat
is de volgende stap voor de achterlopende delen?"

Dat geeft ook een toon: **de architect is al gehoord**. Het advies
hieronder is overwegend *effectuering en afstemming*, niet
*herontwerp*.

---

## §3 Per-model snapshot

Elk blok noemt: kern, cijfers, hoe dit model zich verhoudt tot de §2-
basis, dominante route(s), openstaande punten.

### L1 — Vermogensmodel (micro: individu)

Causaal netwerkmodel van 29 structurele menselijke vermogens; hypothese-
vormend, niet voorspellend, bewust geen emoties of situationele
factoren.

**Cijfers:** 29 nodes · 99 edges · 4 contextsliders · 6 clusters · 204
literatuurbronnen · 61× A-level, 34× AUDIT, 4× B-level evidence.

**Verhouding tot §2-basis:** Volgt het gelaagd slider-inventaris:
A16-A19 zijn bedoeld als L1-projectie van L2-stocks (werkdruk,
teamstabiliteit, normatieve druk, psychologische veiligheid).
Curve-vocabulaire volledig geïmplementeerd (alle vier vormen). Edge-
typologie is eigen 5-set (FOUNDATIONAL/MEDIATING/SOCIAL_REGULATORY/
STRUCTURAL/FEEDBACK) die past bij *systemische rol* — niet bij de
actiewerkwoorden van A_. Stock-onderscheid: niet van toepassing op L1
zelf (vermogens zijn geen stocks), wel als principe voor de
slider-keuze.

**Dominante route:** A (LLM-context). Case Capture Canvas + Case
Respons Template zijn af; de authoring-kant (agent-briefings) werkt,
4 van 29 vermogens uitgewerkt. Ontbreekt: een runner die capture +
model + respons-template tot één LLM-sessie combineert.

**Open:** Empirische gewichtskalibratie (gepland, niet uitgevoerd).
Interventie-catalogus (MX-serie) staat naast de graaf in plaats van
eraan gekoppeld.

### L2 — Affectief Vitale Vereniging (meso: organisatie)

v1.0 gevalideerd model van collectieve vermogens van sportverenigingen,
inclusief een complete diagnose-pipeline van vragenlijst tot
interventie-advies.

**Cijfers:** 21 nodes · 76 edges · 8 sliders · 6 verenigingsprofielen ·
15 interventiepakketten · 97 literatuurbronnen.

**Verhouding tot §2-basis:** Edge-typologie is 3-set (FOUNDATIONAL/
MEDIATING/MODERATING), kleinste vocabulaire van de familie. Slider-set
van 8 komt deels uit L3 (scenario-assen als context) en bevat deels
stocks (psychologische veiligheid, prestatiecultuur) die volgens de
v0.2-notitie gehertypeerd zouden moeten worden. Curve-vocabulaire
deels aanwezig.

**Dominante route:** A en B gecombineerd via de diagnose-pipeline:
vragenlijst → scoring → profielmatching → interventieadvies is
deterministisch, maar kan met een LLM verrijkt worden tot een
gespreksvorm. Interactieve web-variant in backlog.

**Open:** Veldtoetsing niet gedaan. Bewust geen git tot v1.1. Zes
citatie-issues geaccepteerd. De stock-hertypering uit v0.2 niet
doorgevoerd.

### L3 — NSkiV (macro: bondsstrategie)

Strategisch systeemmodel voor het NSkiV Meerjarenbeleidsplan 2026-2030,
met scenario-planning via kwalitatieve context-sliders.

**Cijfers:** 51 nodes · 176 edges · 5 scenario-assen (kwalitatief,
geleidelijk/versneld/disruptief-stijl) · 900 literatuurbronnen · 4
uitgewerkte scenario's · beleidsplan van 52 pagina's met
managementsamenvatting, gespreksleidraad, toelichting systeemmodel.

**Verhouding tot §2-basis:** Edge-typologie is 8-set (enables / drives
/ constrains / threatens / requires / serves / depends_on /
competes_with) — het rijkst qua *actiewerkwoorden*. De 5 sliders zijn
**context-parameters** (externe krachten waar NSkiV niks aan kan
doen), passend in de categorie "externe omgevingsfactoren" uit de
v0.2-notitie. Voedings-infrastructuur (C1/C2/C3-classificatie van
organisatiedocumenten) werkt operationeel — L3 is het enige model met
een lopende data-voeding.

**Dominante route:** A en B (strategisch gesprek). Route C is raamwerk-
klaar maar nog niet gevoed met KPI's. Route D is ver ontwikkeld
(literatuur, checkpoint-rapporten).

**Open:** Geen git. 60% edges zonder directe lit-id-koppeling.
Interactieve slider-app gepauzeerd omdat Max zelf bouwt. Expliciete
koppeling met D1 niet gemaakt.

### D1 — Sportdeelnamemodel (domein, Zeppelin)

Causaal model van factoren voor wedstrijd- en recreatieve
sportdeelname; product-gerichte tweede source-of-truth.

**Cijfers:** 69 nodes · 114 edges · 8 sliders · 66 literatuurbronnen ·
v2.3.0. Dubbele opslag: Modelbouw-zijde = onderzoeksruimte;
Zeppelin-zijde = runtime (FastAPI + D3 + LLM-guard + licentie).

**Verhouding tot §2-basis:** Edge-typologie is Zeppelin-5 (STRUCTURAL/
MEDIATING/MODERATOR/FEEDBACK/SOCIAL_REGULATORY), vergelijkbaar met L1's
categorie *systemische rol*. Slider-set van 8 is nog niet ingebouwd in
het gelaagd slider-inventaris; gedraagt zich als interventie-sliders
(beleidsknoppen) in plaats van context-sliders. Drie van de vier
curves geïmplementeerd in `slider_engine.py` en in de Zeppelin-
simulatie.

**Dominante route:** B (Zeppelin). Route C (data-inventarisatie KNSB,
E04) is kritiek-pad maar nog in backlog. Route A werkt via
Zeppelin's `/reasoning`-endpoint maar beperkt.

**Open:** E04 data-koppeling. Generalisatie naar andere sporten (E14/
E16 nieuwe epics). Explicite verbinding met L3's breedtesport-outcome
node.

### C1 — Capability Model Data-Informed Werken

Inception-fase zijwaartse elaboratie van de L2-capability-node
`data_capability`, met cultuur als stock-node volgens de v0.2-notitie.

**Cijfers:** nog geen JSON-graaf. 16 epics, 85 stories. Literatuur-
verkenning af (6 data-literacy-raamwerken vergeleken). Documentanalyse-
en interview-protocollen klaar.

**Verhouding tot §2-basis:** C1 is het **eerste model dat de v0.2-
notitie als uitgangspunt neemt**: `node_class: stock` voor cultuur,
`role: modererend`, `change_rate: slow`. Nieuwe edge-types
`improves/shapes/determines` volgen het vocabulaire van protocol v0.3
direct. Is in die zin een *testcase* voor hoe v0.3 er uitziet als je
hem echt volgt.

**Dominante route:** nog niet te bepalen — fase te vroeg. A en D zijn
logisch in inception; B en C pas na v1.0-formalisering.

**Open:** Nodes en edges nog te formaliseren (E04/E05/E06). JSON-
conversie (E06) in backlog. Geen visualisatie.

### A_ — Modulaire Modelarchitectuur (protocol-laag)

Gedeelde architectuur: protocol v0.3, referentie-implementaties GVM
(meso) en CSM (macro), en een werkende pipeline.

**Cijfers:** 29/36 stories done. `pipeline.py` = 630 regels, rekent
micro→meso→macro door (25 WP4-items → dimensiescores → 21 vermogens →
6 profielen → 5 uitkomsten → strategische impact). Deterministisch,
geen stochastiek, werkt op GVM+CSM-data.

**Verhouding tot §2-basis:** A_ **is** de §2-basis — de drie documenten
staan hier. Protocol v0.3 zelf claimt 8 edge-types, 4 curve-types, 2
node-classes, evidence A/B/C. GVM + CSM zijn generalisaties van L2 +
L3. Transfer-functies tussen niveaus zijn kwalitatief vastgelegd,
wiskundig nog niet.

**Dominante route:** dient alle routes. A_ is de grammatica waarin
elke andere route zijn zinnen bouwt.

**Open:** GVM_A2_edges.json mechanisch af te leiden maar nog niet
gemaakt. Transfer-functies wiskundig maken. Pipeline-gewichten
ongevalideerd (theoretisch).

---

## §4 Cross-level relaties

### 4.1 Het principe in het kort

De architectuurnotitie formaliseert het uitgangspunt dat de classificatie
van een concept als stock node of slider niet absoluut is, maar
niveau-relatief: *een stock node op niveau N wordt slider op niveau
N-1*. Wat de organisatie intern opbouwt, ervaart het individu als
gegeven context; wat de bond intern opbouwt, ervaart de vereniging als
gegeven omgeving. Externe omgevingsfactoren — economisch klimaat,
regelgeving, seizoen — zijn géén stock nodes op enig niveau en blijven
correct als slider op elk niveau waarop ze relevant zijn.

Dit is geen ontwerpregel die we nog moeten uitvinden; het is een
architecturele positie die al is ingenomen. §4 beschrijft wat het
principe praktisch betekent voor de zes modellen en waar de
nuancering zit die in de notitie nog niet expliciet staat.

### 4.2 Niveau-autonomie blijft het primaat

Het cross-level principe mag **niet** worden gelezen als: "L2 is
afgeleid van L3" of "L1 is afgeleid van L2". De modellen zijn
ontworpen om zelfstandig beantwoordbare vragen te beantwoorden. Een
L2-model moet werken zonder dat bekend is welke strategische keuzes
op L3 zijn gemaakt; een L1-model moet werken zonder dat bekend is in
welke organisatiecontext het individu zich bevindt.

Wat het cross-level principe wél doet, is de **kandidatenlijst** voor
sliders afleidbaar maken. De sliders van niveau N zijn niet
willekeurig: ze komen uit de stock nodes van niveau N+1, *voor zover
relevant* als context voor de vragen die het model op niveau N moet
beantwoorden. De toevoeging "voor zover relevant" is principieel en
draagt de niveau-autonomie: niet elke L3-stock hoeft een L2-slider
te worden, en niet elke L2-stock hoeft een L1-slider te worden. De
analysecontext bepaalt welke kandidaten je activeert.

Praktisch consequence: bij het ontwerpen of herzien van het
slider-landschap van een model begin je met de stock-kandidaten van
het niveau erboven, en daarnaast met de externe omgevingsfactoren.
Vervolgens schrap je wat niet relevant is voor de vragen die dit
model moet beantwoorden. Je bouwt dus niet vanuit niets op, maar je
bent ook niet gebonden aan de volledige bovenliggende stock-lijst.

### 4.3 Gradatie: niet elk macro-thema werkt op elk niveau even hard

Een belangrijke nuancering die in de notitie impliciet zit maar
expliciet gemaakt moet worden: **een macro-thema kan op verschillende
niveaus verschillende zwaarten hebben, of op één niveau zelfs
irrelevant zijn.**

Klimaat en duurzaamheid illustreren dit goed:

- **L3 (NSkiV)**: klimaatverandering is een eerste-orde strategische
  druk — de bond moet vijftien jaar vooruit denken over ledenaantallen
  in een sneeuwarmer Europa. Klimaatdruk is hier een slider die
  expliciet scenariokeuzes opent (hoge/lage klimaatdruk) en doorwerkt
  in strategische capaciteit.

- **L2 (AVV)**: klimaat vertaalt zich in praktische keuzes — wanneer
  trainen we buiten, hoe gaan we om met warmtestress, welke velden zijn
  bespeelbaar. Het is een slider, maar hij opent andere vragen dan op
  L3 en heeft een ander gewicht in de doorwerking.

- **L1 (individueel vermogen)**: klimaat is op individueel niveau vaak
  *niet* als slider relevant — een individu besluit niet over trainen
  onder warmtestress op modelniveau. Het kan als individuele
  omstandigheid meespelen (leeftijdsgerelateerde gevoeligheid voor
  hitte), maar dan is het geen niveau-overstijgende slider, maar een
  case-specifiek attribuut van het casus zelf.

Dit is niet hetzelfde als "L1 negeert klimaat". Het betekent: het
aggregaat "klimaatdruk" hoort niet als slider in het protocol van L1
thuis, omdat de vragen die L1 stelt er niet gevoelig voor zijn.
Wanneer een specifieke L1-casus op klimaat-gevoeligheid uitkomt,
wordt dat in de casus zelf geadresseerd, niet in het generieke
model-protocol.

### 4.4 Consequenties per model-paar

Op basis van §4.1–4.3 zien we de volgende cross-level relaties in de
zes-model-stack:

- **A_ → L2, L3 (GVM, CSM als referentie)**: de architectuur levert de
  grammatica; L2 en L3 zijn implementaties in specifieke sectoren. De
  relatie is protocol-implementatie, niet niveau-hierarchisch.

- **L3 → L2 (NSkiV → AVV)**: strategische bond-keuzes op L3
  (bondsbeleid, regionale structuren, collectieve investeringen) zijn
  kandidaat-sliders voor L2, *voor zover* ze voor vereniging-vragen
  relevant zijn. Niet alle zestien L3-kandidaten hoeven door; de
  expliciete beoordeling per node is nog werk.

- **L2 → L1 (AVV → Vermogensmodel)**: organisatiecultuur,
  psychologische veiligheid, leiderschap zijn stock-kandidaten op L2
  en kandidaat-sliders op L1. De L1-agent briefing raakt dit indirect
  (coach, maar context is al in de casus-capture opgenomen — de mapping
  is nog niet expliciet).

- **D1 ↔ L2**: D1 (sportdeelname, 69 nodes) en L2 (AVV) delen laag en
  sector. De relatie is niet cross-level maar cross-model binnen
  hetzelfde niveau — beide beschrijven meso-dynamiek, maar met
  verschillende afbakeningen (deelname-uitkomst versus
  vereniging-vermogens). Harmonisatie tussen deze twee is een aparte
  ontwerpvraag die niet door het cross-level principe wordt gedekt.

- **C1 ↔ A_**: C1 is een specifieke toepassing van het protocol op
  een smal domein (data-informed beslissen). Het is in dezelfde laag
  als L2, maar thematisch gescheiden. Relatie: co-existentie onder
  hetzelfde protocol.

### 4.5 Wat dit betekent voor de advies-scope

Het cross-level principe is in de architectuurnotitie helder
geformuleerd en wordt niet heroverwogen. De adviesvraag beperkt zich
daarom tot:

1. **Per model-paar de concrete vertaling expliciet maken** —
   welke stock-kandidaten van N+1 worden sliders op N, welke vallen
   af, en met welke reden.
2. **Gradatie bewaken** — niet elk macro-thema mag automatisch
   doorbranden naar het volgende niveau; de relevantie-toets blijft
   per niveau.
3. **Niveau-autonomie bewaken** — geen koppelingen introduceren die
   van L2 een functie-van-L3 maken; het moet blijven staan als
   L3 nog niet is ingevuld of anders wordt ingevuld.

---

## §5 Wat bindt, wat niet

Van de zes modellen is de vraag wat ze *hetzelfde* moeten doen en wat
ze *vrij* mogen invullen. Het protocol v0.3 geeft hierop al antwoord
in de vorm van de architecturale basis (§2). Deze sectie destilleert
het in drie laagjes: wat **moet** uniform zijn, wat **mag** uniform
zijn, en wat **niet** uniform moet zijn.

### 5.1 Wat moet uniform — representatie, niet semantiek

De representatielaag is de smalste en tegelijk belangrijkste bindende
laag. Als modellen deze niet delen, is er geen mechanische uitwisseling
mogelijk, geen gedeelde validator, en geen cross-level pipeline.

Wat moet uniform zijn:

- **Node-structuur**: elke node heeft `id`, `label`, `domain`,
  `node_class` (`regular` of `stock`), en voor stocks een
  `change_rate`. De velden staan, de waarden zijn per model vrij.
- **Edge-structuur**: elke edge heeft `source`, `target`, `edge_type`
  uit het 8-tal, `curve_type` uit het 4-tal, `weight`, `evidence`.
  Edgetypes en curvetypes zijn een gesloten vocabulaire dat door het
  protocol wordt beheerd.
- **Evidence-schaal**: A (sterk), B (matig), C (zwak/expert) is het
  gedeelde referentiekader. Niet alle modellen moeten elke waarde
  gebruiken, maar als ze evidence vermelden moet het uit deze
  verzameling komen.
- **Slider-contract**: elke slider heeft een type (interventie /
  calibratie / context), een skaal, een default, en een beschrijving
  van de doorwerking. Dit contract staat in §6 verder uitgewerkt.

Deze laag is bindend omdat het de grammatica is. Afwijken hiervan is
niet een modelkeuze maar een protocol-wijziging, en hoort dus via de
protocol-governance te lopen, niet via individuele modellen.

### 5.2 Wat mag uniform — gedeeld waar nuttig, eigen waar zinvol

Onder de grammatica zit een laag waar uniformiteit waardevol is maar
niet absoluut. Waar modellen dezelfde dingen beschrijven, is het
nuttig dezelfde woorden te gebruiken; waar ze verschillende dingen
beschrijven, is uniformiteit kunstmatig.

Wat mag uniform:

- **Macro-slider-vocabulaire**: klimaatdruk, economisch klimaat,
  normatieve cultuurdruk — als twee modellen deze sliders beide
  gebruiken, hoort ze dezelfde naam, schaal en (grofweg) doorwerking
  te hebben. Als maar één model hem gebruikt, is dat geen probleem.
- **Domain-taxonomie**: de 9 domeinen in D1 en de 5 dimensies in GVM
  zijn verschillende indelingen van hetzelfde onderliggende domein
  (sport-meso). Er is waarde in het expliciet mappen van de twee,
  maar niet in het afdwingen van één indeling over alle modellen.
- **Stock-register op niveau**: de lijst van stock-kandidaten op L2
  (cultuur, psychologische veiligheid, collectieve datavaardigheid,
  leiderschapsvertrouwen) kan gedeeld worden tussen AVV, GVM en D1 —
  ze zitten allemaal op het meso-niveau. Welke ze activeren is model-
  specifiek; dat ze uit een gedeeld register komen, is efficiënt.

Deze laag verloopt via conventie en coördinatie, niet via afdwingen.
Gedeeld register bijhouden, cross-model review bij introductie van
nieuwe macro-sliders — zo ontstaat uniformiteit waar het telt, zonder
dat elk model zich aan de keuzes van andere modellen moet binden.

### 5.3 Wat niet uniform — domein, diepgang, tempo

Onder de representatie- en vocabulaire-laag zit de inhoud, en daar
hoort uniformiteit niet thuis. Elk model heeft een eigen vraag, een
eigen sector, een eigen rijpingstempo.

Wat niet uniform moet zijn:

- **Welke nodes in het model zitten**: L3 heeft 22 nodes, D1 heeft
  69, L2 heeft 21 vermogens. De omvang volgt uit de vraag, niet uit
  een gedeelde standaard.
- **Welke wiskundige parameters**: curve-shape per edge is case-
  specifiek. `INVERTED_U` voor trainingsbelasting → prestatie heeft
  andere parameters dan `INVERTED_U` voor regeldruk → capability.
  Het curve-type is gedeeld, de parametrisatie niet.
- **Welke evidence per edge**: elk model bouwt zijn eigen evidence-
  basis. Literatuur die L3 autoriteit geeft, zegt niets over L2.
- **Tempo en rijpheidsniveau**: L3 is conceptueel, L2 runnable, D1
  in productie. Proberen te synchroniseren vertraagt allemaal.
- **Ontwikkelfocus**: welke route (§7) een model het hardst dient,
  bepaalt waar het als eerste in rijpt. Dat mag verschillen.

### 5.4 De samenhang op één lijn

```
moet uniform   = representatie (schema, edgetypes, curvetypes,
                 evidence-schaal, slider-contract)
mag uniform    = gedeeld vocabulaire waar modellen elkaar raken
                 (macro-sliders, stock-registers, domein-mapping)
niet uniform   = inhoud (welke nodes, welke parameters, welke
                 evidence, welk tempo)
```

De protocol-laag (A_) beheert "moet". De modellen-coördinatie beheert
"mag". De modellen zelf beheren "niet".

---

## §6 Slider-landschap

Van de zes modellen heeft de architectuurnotitie plus het
slider-inventaris (E05/S03) het slider-landschap al voor een groot
deel in kaart gebracht. Deze sectie vat samen wat er ligt en welke
consequenties dat heeft voor de andere modellen.

### 6.1 Drie typen sliders

Niet elke slider is hetzelfde. Het onderscheid is relevant omdat de
drie typen verschillend worden gebruikt in een casus.

- **Interventie-sliders**: vertegenwoordigen een keuze die de
  modelgebruiker kan maken. Voorbeelden: investering in
  cultuurontwikkeling, intensiveren van leiderschapstraining. De
  slider representeert een hypothetische handeling; de uitkomst
  geeft de verwachte doorwerking.
- **Calibratie-sliders**: vertegenwoordigen onzekerheid over een
  parameter die buiten de controle van de gebruiker valt. Voorbeelden:
  sterkte van een bepaalde causale relatie, gevoeligheid van een
  uitkomst voor een voorwaarde. Worden gebruikt voor robustness-
  checks, niet voor scenario-verkenning.
- **Context-sliders**: vertegenwoordigen externe omgevingscondities
  of hoger-liggende niveau-stocks. Voorbeelden: klimaatdruk,
  economisch klimaat, collectieve sectorcultuur. Worden gebruikt om
  de casus in een context te plaatsen.

Deze driedeling is voor alle modellen relevant, maar de verhouding
verschilt per model. L3 leunt zwaar op context-sliders (strategische
scenario's); L2 op interventie- en context-sliders; L1 vooral op
interventie-sliders (met de organisatiecontext als case-input, niet
als slider).

### 6.2 Wat het slider-inventaris al vastlegt

E05/S03 heeft een 17-sliders-inventaris opgeleverd voor de
architectuur-referentie-implementaties (GVM, CSM). Elke slider is
gedocumenteerd met:

- Type (interventie / calibratie / context)
- Niveau waarop hij werkt (macro / meso / micro)
- Afgeleide status (welke bovenliggende stock hij instantieert, indien
  van toepassing)
- Schaal en default
- Doorwerkingsketen (welke nodes en edges hij raakt, met welke curve-
  vorm)

Dit is geen modelkeuze maar een protocolkeuze — het slider-contract
ligt vast en wordt overgenomen door modellen die het protocol volgen.

### 6.3 Consequenties voor de overige modellen

De andere modellen hebben sliders die tegen dit gedeelde contract
moeten worden gelegd. Praktische observaties:

- **L3 (NSkiV)**: heeft een eigen sliders-context-document dat deels
  overlapt met het protocol-inventaris (klimaat, economie, normatieve
  druk). Mapping expliciet maken is waardevol — dan zie je of L3
  dezelfde macro-sliders anders calibreert, of dat er genuine L3-
  specifieke sliders zijn.
- **L2 (AVV) + D1 (Sportdeelname)**: delen het meso-niveau. Als hun
  sliders-inventarissen niet op elkaar aansluiten, wordt cross-model
  reasoning moeilijk. Mapping + conflictdetectie is hier een
  concrete bruggebouw-actie.
- **L1 (Vermogensmodel)**: volgens het cross-level principe zijn L1-
  sliders de relevante subset van L2-stocks plus externe omgevings-
  factoren. Op dit moment bevat de L1-briefing nog geen expliciete
  slider-laag — de organisatiecontext wordt in de casus-capture
  opgenomen, niet als parametrische slider. Of dat bewust is of een
  openstaande ontwerpvraag is, is één van de open punten.
- **C1 (Data-informed)**: thematisch smal; heeft waarschijnlijk een
  kleine, specifieke sliderset. Belangrijk dat deze aansluit op het
  protocol-contract, niet dat hij uitgebreid is.

### 6.4 Samenvatting — het slider-beheer is een coördinatievraag

Het slider-landschap is technisch geregeld via het protocol
(representatie) en semantisch nog niet volledig op elkaar afgestemd
(betekenis per model). Dat is precies de "mag uniform"-laag uit §5.2.

De bruggenbouw-actie hier is niet "één slider-lijst voor alle
modellen", maar "een cross-model slider-register waarin per
gezamenlijke slider de afstemming expliciet wordt gemaakt" — inclusief
notes waar twee modellen bewust andere defaults of doorwerkingen
hanteren.

---

## §7 Vier use-case routes

Modellen zijn *modellen* — ze kunnen op verschillende manieren nuttig
zijn. De vier routes die in §1.3 werden geïntroduceerd zijn niet
concurrerende alternatieven; ze vertegenwoordigen verschillende
manieren waarop een model waarde levert. Elk model heeft een
dominante route op enig moment, maar kan in zijn levensloop door
meerdere routes bewegen.

De routes zijn bewust onderscheiden omdat ze verschillende eisen aan
het model stellen. Een model dat primair voor route A (authoring)
wordt ingezet hoeft niet runnable te zijn; een model voor route C
(LLM-reasoning over casus) moet uitstekend instrumenteerbaar zijn. De
routes bepalen waar ontwikkel-energie naartoe gaat.

### 7.1 Route A — Authoring & agent-briefing

**Vraag die de route beantwoordt:** hoe geeft dit model een LLM-agent
de context om over een sectordomein te redeneren?

**Wat je ervoor nodig hebt:**

- Een gestructureerde briefing die het domein, de kernconcepten, de
  taal en de kaders benoemt.
- Expliciete do's en don'ts voor de LLM (tone of voice, welke
  aannames vermijden, welke bronnen hanteren).
- Een casus-capture sjabloon zodat de LLM weet welke input hij krijgt.
- Een casus-respons sjabloon zodat de LLM weet welke output hij moet
  leveren.
- Koppeling naar het onderliggende causale model als naslagwerk —
  niet als uitvoerend algoritme.

**Rijpheidsteken:** de agent kan zonder jou een casus doorlopen en
komt met analyses die domeinexpertise weerspiegelen, niet
generiek-plausibele LLM-output.

**Modellen waarvoor deze route primair is:** L1 (vermogen — agent-
briefing bestaat al, templates zijn leidend), D1 (sportdeelname —
als beleidsverkenner is authoring de primaire output). In
inception-fase is route A ook voor L3 de logische eerste stap.

**Wat de route niet nodig heeft:** runnable wiskunde, numerieke
doorrekening, pipeline-integratie.

### 7.2 Route B — Model-als-ground-truth

**Vraag die de route beantwoordt:** wat is in dit domein inhoudelijk
juist volgens de stand van kennis?

**Wat je ervoor nodig hebt:**

- Gevalideerd causaal model met evidence-onderbouwing per edge.
- Explicitering van wat aannames zijn versus empirisch onderbouwd.
- Literatuurverwijzingen per relatie, niet alleen in een algemene
  bibliografie.
- Review door domein-experts (niet alleen ontwerpers).
- Conflictresolutie tussen modellen die hetzelfde zeggen — welke
  geldt, en waarom.

**Rijpheidsteken:** een onafhankelijk domeinexpert kan het model
openen en zonder uitleg zien wat erin staat, wat bronnen zijn, en
waar hij het mee eens of oneens is.

**Modellen waarvoor deze route primair is:** A_/GVM als referentie-
implementatie (bewijs dat het protocol werkt in een domein), L2 (AVV
— vermogensmodel voor vereniging als domein-authoritatieve stapeling
van vermogens). In volwassen toestand bewegen alle modellen gedeeltelijk
richting deze route.

**Wat de route niet nodig heeft:** runnability, UI, live-interactie.
De output is statisch kennisartefact.

### 7.3 Route C — LLM-reasoning over casus

**Vraag die de route beantwoordt:** geef mij, gegeven deze concrete
casus, een doordachte analyse van wat er speelt en welke interventies
zinvol zijn.

**Wat je ervoor nodig hebt:**

- Het model in een vorm die een LLM kan raadplegen tijdens redeneren
  (geserialiseerd schema, of een MCP-achtige interface naar de
  pipeline).
- Casus-capture dat de LLM gestructureerd kan invullen uit gesprek
  met de gebruiker.
- Een doorrekenings-mechanisme dat de LLM kan aanroepen ("wat
  gebeurt er als ik deze slider op X zet?").
- Respons-sjabloon dat bewaakt dat de LLM-analyse teruggrijpt op de
  modeldynamiek en niet vrij speculeert.
- Guardrails: wat mag de LLM wel en niet interpreteren, waar moet hij
  terugvallen op "dit weet het model niet".

**Rijpheidsteken:** een beleidsmedewerker kan een casus in natuurlijke
taal voorleggen, krijgt een analyse die traceerbaar is tot het model,
en kan interventie-effecten doorrekenen in het gesprek.

**Modellen waarvoor deze route primair is:** D1 (Graaf Zeppelin is
precies deze route — beleidsverkenner voor sportdeelname), en op
termijn L2 (AVV als LLM-tool voor bestuurders van verenigingen).

**Wat de route niet nodig heeft:** dat de LLM volledig autonoom werkt
— menselijk oordeel blijft aanwezig; het model is instrument, niet
orakel.

### 7.4 Route D — Deterministische pipeline

**Vraag die de route beantwoordt:** gegeven een gestandaardiseerde
set inputs, wat is de uitkomst van het causale systeem?

**Wat je ervoor nodig hebt:**

- Complete, gesloten grafiek — alle edges gewogen, alle curves
  geparametriseerd.
- Deterministisch doorrekenalgoritme (geen stochastiek, geen
  LLM-interpretatie onderweg).
- Validatielaag die detecteert wanneer inputs buiten het
  toepassingsgebied vallen.
- Versionering zodat uitkomsten over tijd reproduceerbaar zijn.
- Testsuite die regressies voorkomt bij protocol- of data-wijzigingen.

**Rijpheidsteken:** dezelfde casus-input levert tot op de cijfers
dezelfde output op, en bij parameter-wijzigingen is te verantwoorden
wat waarom is veranderd.

**Modellen waarvoor deze route primair is:** A_/pipeline.py
(micro→meso→macro doorrekening, CSM+GVM-data, 630 regels
deterministisch). In vollere vorm ook voor L3 als beleidssimulator
voor bondsstrategie op termijn.

**Wat de route niet nodig heeft:** LLM-interactie, natuurlijke-taal-
interface, open-einde redenering. De waarde zit in reproduceerbaarheid.

### 7.5 Routes en rijping — waarom de volgorde uitmaakt

Een model kan niet alle routes tegelijk even hard bedienen. In de
praktijk zien we een terugkerend patroon:

1. **Route A (authoring) eerst**: in inception-fase is de vraag niet
   "is dit runnable?" maar "staat het domein?". Agent-briefing en
   templates dwingen expliciete articulatie van kernconcepten af.
2. **Route B (ground-truth) parallel of kort erna**: zodra het
   domein staat, komt de vraag van empirische onderbouwing. Evidence
   wordt toegevoegd; experts reviewen.
3. **Route C (LLM-reasoning) bij rijping**: met een onderbouwd model
   en een gevalideerde briefing kun je een LLM over casus laten
   redeneren zonder dat hij hallucineert.
4. **Route D (pipeline) bij volwassenheid**: deterministische
   doorrekening vereist de meeste discipline — alle parameters
   onderbouwd, gesloten grafiek, regressietests. Dit is
   eindfase-werk.

Dit is een *patroon*, geen verplichte volgorde. A_ heeft route D in
werkende vorm terwijl routes A en C nog lichtere aanwezigheid
hebben; dat is een geldige keuze. L3 zit in route A (inception);
probeer daar geen route D te forceren. D1 balanceert routes A en C
(Graaf Zeppelin als beleidsverkenner); de pipeline-route is daar nog
niet het doel.

Het advies hieronder (§8) houdt per model rekening met de dominante
route en stelt bruggenbouw-acties voor die bij die fase passen.

---

## §8 Harmonisatie-voorstellen

De architecturale basis ligt er; het cross-level principe is
geformaliseerd; het slider-landschap is gedeeltelijk in kaart. Deze
sectie vertaalt dat naar concrete bruggenbouw-acties per model en
cross-model, geordend naar dominante route (§7) en respecteert
waarbij de modellen nu staan — geen rijping forceren waar de route
dat niet vraagt.

De voorstellen zijn geformuleerd als kandidaat-acties, niet als
voorschrift. De prioritering (§9) maakt expliciet welke eerst
nuttig zijn.

### 8.1 Per model — concrete acties

**L1 — Vermogensmodel (route A primair)**

1. Expliciteer of de L1-slider-laag bewust leeg is (context via
   casus-capture) of een openstaande ontwerpvraag. Dit raakt §6.3 en
   bepaalt of route C op termijn haalbaar is.
2. Maak de mapping tussen L1-concepten en het L2-stock-register
   expliciet — welke L2-stocks landen als L1-context, welke niet, en
   op welke grond (§4.4).
3. Bewaak dat agent-briefing en casus-respons templates gesynchroniseerd
   blijven met protocol-updates (A_/v0.4 zou L1 raken als evidence-
   schaal of edgetypes wijzigen).

**L2 — AVV / Vermogensmodel Vereniging (route A + B)**

1. Leg het 21-vermogens-schema langs het GVM-referentie-schema (GVM is
   de generalisatie van L2). Conflictdetectie: waar wijkt L2 bewust af,
   waar is het onbedoeld?
2. Voer de stock-vs-slider-toets uit op de huidige L2-sliders
   (architectuurnotitie §5). Resultaat: per slider de classificatie
   geëxpliciteerd.
3. Evidence-laag opbouwen richting route B: welke van de 21
   vermogens hebben literatuur-onderbouwing, welke expert judgement.

**L3 — NSkiV (route A primair, inception)**

1. Casus-capture en casus-respons templates opstellen naar model van
   L1 — dat dwingt strategische vragen expliciet uit en maakt de
   agent-briefing werkbaar.
2. De 22-nodes-set consolideren: welke zijn stock (bv. leden-loyaliteit,
   infrastructuur-basis), welke capability, welke uitkomst. Dit
   bereidt route B later voor.
3. Slider-context-document langs het A_/protocol-slider-inventaris
   leggen (§6.3). Welke sliders zijn genuine L3-specifiek, welke
   instantiëren protocol-sliders?

**D1 — Sportdeelname (route A + C, productie)**

1. Cross-model slider-register opzetten met L2 als eerste counterpart
   (zelfde meso-niveau). Map elke D1-slider op L2-equivalent; waar
   mismatch, expliciet beredeneren.
2. ID-schema-migratie (inmiddels done voor data/models) doortrekken
   waar nog niet: scripts, exports, externe artefacten.
3. Graaf Zeppelin-LLM-interactie-patroon documenteren als template
   voor route C in andere modellen (vooral L2 op termijn).
4. Evidence-kolom aanvullen waar die nu leeg is, vooral op de
   culturele edges die in de architectuurnotitie als stock-candidates
   zijn geïdentificeerd.

**C1 — Data-informed beslissen (route A + B, specifiek domein)**

1. Sliders toetsen tegen protocol-inventaris (§6.3). C1 is thematisch
   smal — de toets zou kort moeten zijn, en leveren wat wel/niet
   nodig is.
2. Positionering t.o.v. L2 helder maken: is C1 een L2-variant, een
   L2-aanvulling, of een apart niveau? Dit bepaalt of het onder
   L2-protocol-updates meebeweegt of eigen ritme houdt.

**A_ — Architectuur (protocol-laag)**

1. GVM_A2_edges.json mechanisch afleiden en in commits vastleggen.
2. Transfer-functies tussen niveaus van kwalitatief naar wiskundig
   brengen (of expliciet markeren dat dat niet op de roadmap staat).
3. Pipeline-gewichten valideren — theoretisch nu, empirisch in
   toekomst. Minimaal: documenteren wat theoretisch is en welke
   validatie-actie ervoor nodig is.
4. Protocol-governance: procedure voor v0.4 en verder. Wie kan een
   protocol-change voorstellen, welke modellen worden impact-
   assessed, hoe wordt backward-compatibility gehanteerd.

### 8.2 Cross-model — gedeelde infrastructuur

Naast per-model werk zijn er een paar acties die alleen zin hebben
als ze cross-model worden gedaan:

1. **Cross-model slider-register**: één plek waar elke slider die in
   meer dan één model voorkomt, wordt gedocumenteerd. Minimaal:
   naam, schaal, defaults per model, en expliciete notes bij
   afwijkingen (§6.4). Eigenaar: A_ (protocol-laag).
2. **Stock-node-register per niveau**: voor L2 en L3 een gedeelde
   lijst van stock-kandidaten die elk model kan activeren. Dit
   operationaliseert §5.2 (mag uniform) en ondersteunt het
   cross-level principe (§4.2).
3. **Domein-taxonomie-mapping**: de 9 domeinen van D1 en de 5
   dimensies van GVM expliciet op elkaar mappen. Niet om één indeling
   af te dwingen, maar om kruisverwijzing tussen modellen mogelijk
   te maken.
4. **Evidence-bibliografie gedeeld**: literatuur die in meer dan één
   model relevant is, wordt centraal bijgehouden. Modellen verwijzen
   ernaar; updates stromen door. Voorkomt divergerende evidence-
   claims over dezelfde bron.
5. **Protocol-release-kalender**: welke protocol-versie wanneer,
   welke modellen implementeren op welk tempo. Ondersteunt
   niveau-autonomie (modellen kunnen achterblijven bij de laatste
   versie als hun route dat rechtvaardigt) en voorkomt
   onzichtbare versiedrift.

### 8.3 Conflict-resolutie — hoe omgaan met botsingen

Bij cross-model mapping zullen onvermijdelijk conflicten opduiken:
een slider die in twee modellen andere schalen heeft, een domein-
node die in het ene model als mediator en in het andere als
moderator is geclassificeerd, of evidence die per model anders wordt
geïnterpreteerd.

Een handzame beslisvolgorde:

1. **Is het een protocol-vraag of een modelvraag?** Protocol-vragen
   (edgetypes, curvetypes, schemavelden) gaan naar A_. Modelvragen
   blijven bij het model.
2. **Is er een empirische basis?** Literatuur wint van expert
   judgement; expert-consensus wint van eenzijdige interpretatie.
3. **Is er een niveau-relevantie-verschil?** Dezelfde node kan op
   verschillende niveaus verschillend functioneren; dat is legitiem,
   geen conflict (zie §4.3).
4. **Bij blijvend conflict**: documenteer de keuze expliciet in het
   betreffende register met datum, argumentatie en betrokken modellen.
   Geen stille vervagings-convergenties — als twee modellen bewust
   divergeren, moet dat zichtbaar zijn.

### 8.4 Wat niet te doen

Ter afbakening, een paar bewust niet-opgenomen acties:

- **Geen grote rewrite van bestaande modellen om protocol-conform te
  worden**. Modellen rijpen in hun eigen tempo; protocol-adoption is
  incrementeel.
- **Geen geforceerde route-verbreding**. Als L3 in inception staat,
  bouw daar niet alvast een route-D-pipeline. De routes zijn volgorde-
  gevoelig (§7.5).
- **Geen "master-model" waarin alle andere worden opgelost**. Elk
  model beantwoordt een eigen vraag; convergentie is geen doel op
  zich.
- **Geen premature harmonisatie van evidence**. Laat modellen eerst
  hun eigen evidence-basis opbouwen; cross-model consolidatie komt
  bij route-B-rijping, niet nu.

---

## §9 Openstaande beslissingen

De voorstellen in §8 leunen op een aantal keuzes die nog niet zijn
gemaakt. Deze sectie maakt ze expliciet zodat de besluitvorming kan
gebeuren zonder dat de acties onderhand gaan wringen.

### 9.1 Beslissingen over scope en eigenaarschap

**B1 — Eigenaarschap van de cross-model registers.**
Wie beheert het cross-model slider-register, het stock-node-register,
de domein-taxonomie-mapping? Mogelijkheden:

- A_ (protocol-laag) beheert alles. Voordeel: één plek, consistente
  governance. Nadeel: belasting op A_ neemt toe, en sommige registers
  zijn eerder coördinatie dan protocol.
- Per register een andere eigenaar. Voordeel: lastverdeling. Nadeel:
  meer overleg nodig.
- Lichte coördinatie-laag naast A_ (bv. "modellen-board"). Voordeel:
  schaalt. Nadeel: overhead.

*Voorstel ter keuze, geen vastgesteld standpunt.*

**B2 — Snelheid en volgorde van mapping-acties.**
§8 noemt zeker tien mapping-acties. Volgorde-advies:

1. Eerst D1 ↔ L2 (zelfde niveau, meest directe overlap).
2. Daarna L3 sliders ↔ protocol-inventaris (hoogste strategisch
   gewicht).
3. Dan L2 stock-vs-slider-toets.
4. Vervolgens L1 ↔ L2 mapping (cross-level).
5. C1-positionering als achtervolger.

Dit is een voorstel; de keuze om één van deze te prioriteren ligt
bij de eigenaar van de betreffende modellen.

**B3 — Tempo van protocol-rijping.**
A_ staat op v0.3. Wat triggert v0.4? Mogelijk triggers:

- Transfer-functies wiskundig vaststellen (nu kwalitatief).
- Protocol-governance-procedure formaliseren.
- Een specifiek probleem uit een van de modellen dat protocol-
  aanpassing vraagt.

Een *waardenvraag*: rijp het protocol pas wanneer een concrete
modelbehoefte daarom vraagt (pull), of proactief (push) om modellen
richting te geven?

### 9.2 Beslissingen over route-commitment per model

**B4 — L1 slider-laag expliciet maken.**
Op dit moment zit de organisatiecontext in de casus-capture, niet als
parametrische slider. Twee opties:

- Bewust zo laten. L1-casussen zijn individueel, context is altijd
  concreet, parametrische sliders voegen abstractie toe die de
  LLM-route eerder hindert dan helpt.
- Sliders introduceren om route C (LLM-reasoning) later mogelijk te
  maken. Dan moet de mapping met L2-stocks helder worden (§4.4).

De keuze hangt af van of L1 als route-A-only (authoring) blijft of
doorgroeit naar route C. Dat is zelf een inhoudelijke beslissing.

**B5 — D1 — welke volgende route-stap.**
D1/Graaf Zeppelin is sterk in routes A en C. De vraag is of route B
(evidence-versteviging) of route D (pipeline) de volgende prioriteit
krijgt. Route D is ambitieus gezien de 69-nodes-set; route B is
laagdrempeliger maar vraagt expert-coördinatie.

**B6 — L3 eerste deelmodel.**
L3 staat in inception. Optie: eerst een deelmodel volledig afmaken
(bv. "ledenbinding" of "infrastructuur") voordat de hele 22-nodes-set
wordt doorontwikkeld. Dat levert een werkbaar prototype op route A
zonder dat alles moet wachten op volledigheid.

### 9.3 Beslissingen over conflicterende concepten

**B7 — Stockscope voor L1.**
De architectuurnotitie is duidelijk over stocks op L2 (organisatie-
niveau: cultuur, leiderschap). Op L1-niveau is het minder helder:
zijn er persoonlijke stocks (zelfvertrouwen, identiteit, trauma's)
die als interne toestandsvariabelen op individueel niveau functioneren?
Of behandelt L1 het individu als momentopname en zijn stocks daar
niet relevant?

**B8 — Positionering C1 t.o.v. L2.**
Zie §8.1 (C1, punt 2). Keuze: C1 als L2-variant, L2-aanvulling, of
apart niveau.

**B9 — Stock-vs-slider hertypering.**
De architectuurnotitie geeft een kandidatenlijst van huidige sliders
die mogelijk stocks zijn (psychologische veiligheid, prestatiecultuur,
nader te bepalen: sportidentiteit, ouderbetrokkenheid). Wie voert de
inhoudelijke beoordeling uit, en met welke review?

### 9.4 Samengevat

```
Scope en eigenaarschap  : B1, B2, B3
Route-commitment        : B4, B5, B6
Conceptuele conflicten  : B7, B8, B9
```

Deze beslissingen hoeven niet allemaal tegelijk te worden genomen;
enkele kunnen wachten tot hun context rijper is (B3, B5). Andere zijn
blokkerend voor §8-acties (B1 voor de registers, B9 voor de L2-
slider-toets).

---

## §10 Afsluiting

Deze verkenning stelt geen nieuwe architectuur voor. De architectuur
ligt er al: protocol v0.3, het stock-nodes-slider-cultuur-principe,
het slider-inventaris, GVM en CSM als referentie-implementaties, de
werkende pipeline. Wat dit document doet, is de resterende
coördinatievragen rond die basis expliciteren en de bruggenbouw tussen
de zes modellen in concrete acties vatten.

De centrale observatie is dat de zes modellen niet in één model hoeven
op te gaan. Ze beantwoorden eigen vragen in eigen niveaus, en hun
waarde zit in de combinatie: L1 voor individuele redeneringen, L2/D1
voor meso-dynamiek, L3 voor strategische horizon, A_ als grammatica,
C1 als specifieke toepassing. Het protocol dat ze bindt is smal
(representatie, edgetypes, curvetypes, evidence-schaal) en laat
inhoudelijke vrijheid zo breed als de modellen nodig hebben.

De cross-level relatie — "stock op niveau N wordt slider op niveau
N-1" — is geformaliseerd maar niet in beton gegoten: niveau-autonomie
blijft het primaat, en niet elk macro-thema werkt op elk niveau even
hard. De vier use-case routes (authoring, ground-truth, LLM-reasoning,
pipeline) geven per model richting aan waar de ontwikkelenergie het
best naartoe gaat, zonder uniformiteit te forceren waar die niet
past.

Concreet zijn de eerste drie acties die zonder veel voorbereiding
waarde opleveren:

1. D1 ↔ L2 slider-mapping — zelfde niveau, directe overlap, levert
   meteen zichtbaarheid van afwijkingen op.
2. L2 stock-vs-slider-toets — de architectuurnotitie geeft de
   methodiek; uitvoering is een inhoudelijke review-ronde.
3. L3 casus-capture + casus-respons templates — brengt L3 op een
   werkbaar niveau voor route A.

Dit is een begin; de volle lijst (§8) vraagt langer werk en
prioritering via §9. Wat dit document wil bereiken is dat die
prioritering met het volledige beeld voor ogen kan gebeuren, en dat
niemand meer hoeft uit te vinden wat al is uitgevonden.

---

*Versie 2 van deze verkenning is een integrale herziening; versie 1 is
vervangen, niet aangevuld. De verhouding tot het protocol (A_) is:
dit document volgt het protocol, stelt het niet voor. Openstaande
beslissingen in §9 kunnen via de protocol-governance lopen (B1, B3)
of via de modellen zelf (overige).*
