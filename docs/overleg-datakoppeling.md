# Overleg: graaf koppelen aan echte data

Voorbereiding voor het gesprek over datakoppeling van het sportdeelname-model.

## Voor wie leest dit?

Dit stuk is voor beide gesprekspartners. Als je nog niet met "grafen" hebt
gewerkt, lees dan eerst hoofdstuk 1. Ken je het model al? Spring naar
hoofdstuk 3 (de node-audit tabel).

---

## 1. Wat is een graaf — in het kort

Een **graaf** is een model van factoren en hun onderlinge relaties. Je kunt
het zien als een landkaart:

- **Nodes** zijn de plaatsen op de kaart. In ons model is een node een
  factor die met sportdeelname te maken heeft, bijvoorbeeld "Financiële
  draagkracht" of "Clubklimaat".
- **Edges** zijn de wegen tussen de plaatsen. Ze laten zien welke factor
  welke andere factor beïnvloedt. Bij elke edge hoort een richting
  (positief of negatief) en een sterkte (zwak, midden, sterk).

Ons model heeft **69 nodes** en **114 edges**, verdeeld over **9 domeinen**
(zoals Psychologisch, Sociaal, Macro-context) en **5 niveaus** (L0 tot en
met L3). Die niveaus helpen bij het lezen van de kaart:

| Niveau | Betekenis                             | Voorbeeld               |
|--------|---------------------------------------|-------------------------|
| L0     | Einduitkomsten                        | Feitelijke deelname     |
| L1     | Directe factoren op de deelnemer      | Intrinsieke motivatie   |
| L2     | Organisatie rond de deelnemer         | Coachkwaliteit          |
| L3     | Brede context                         | Economisch klimaat      |

Het model is tot nu toe gebaseerd op **wetenschappelijke literatuur**. De
edges zijn onderbouwd met bronnen, maar nog niet gecontroleerd met echte
cijfers of ervaringen uit het veld. Dat is de volgende stap.

---

## 2. Waarom koppelen aan data?

De graaf is nu een logisch verhaal: "als A omhoog gaat, verwachten we dat
B omlaag gaat". Met data kunnen we twee dingen doen:

1. **Toetsen of de literatuur klopt voor onze context.** Een effect uit een
   Engels onderzoek is niet altijd even sterk in Nederland of bij
   schaatsen.
2. **De sterkte van relaties leren uit echte cijfers.** De app kan dan
   betere simulaties maken.

Maar: **we hebben lang niet voor elke node data.** Sommige factoren zijn
lastig te meten (bijvoorbeeld "Intrinsieke motivatie"). Andere hebben we
direct beschikbaar uit KNSB-systemen (bijvoorbeeld "Licentiestatus").

Daarom moeten we kiezen: **wat doen we eerst, en wat doen we misschien
nooit?**

---

## 3. Node-audit tabel (gespreksinstrument)

Dit is de hoofdtabel voor het overleg. De lege kolommen rechts vullen we
samen in.

### Kolommen uitgelegd

- **Prio**: voorgestelde prioriteit voor datakoppeling. Binnen de hoogste
  prioriteit hebben we nog een volgorde aangebracht (A1 / A2 / A3),
  zodat we niet "alles-of-niets" met 42 nodes tegelijk hoeven beginnen.
  - **A1 — Grondslag (12 nodes)**. Zonder deze kunnen we niet valideren
    en geen demo doen. De 4 uitkomstnodes (L0), plus nodes waar bond=hoog
    én een slider samenvallen (dubbel strategisch).
  - **A2 — Eerste paden (17 nodes)**. Genoeg om een aantal slider → L0
    paden sluitend te krijgen. Overige bond=hoog nodes, overige
    slider-gekoppelde L1-nodes, en hubs binnen A.
  - **A3 — Breedte-uitbouw (13 nodes)**. Minder urgent. Vooral
    slider-gekoppelde macronodes (CBS / KNMI, makkelijk later op te halen)
    en geïsoleerde nodes met lage degree.
  - **B — middelhoog (17 nodes)**. Belangrijk tussenstation, vaak veel
    verbindingen.
  - **C — lage prioriteit (10 nodes)**. Perifeer, weinig invloed, of
    moeilijk meetbaar. Kan later of blijft literatuur-only.
- **KNSB kan sturen**: "hoog/midden/laag/geen". Geeft aan of beleid van de
  bond deze factor kan beïnvloeden.
- **Sliders**: de beleidsknoppen in de app die deze node raken. Een node
  met een slider-link is belangrijker om te meten, omdat de gebruiker
  eraan draait.
- **Edges in/uit**: aantal inkomende en uitgaande verbindingen. Veel
  verbindingen = een knooppunt (hub) — meetfouten hier werken ver door.
- **Datatype (kw/qu)**: kwantitatief (getallen) of kwalitatief (interviews,
  surveys). **In te vullen tijdens overleg.**
- **Mogelijke bron**: waar kunnen we de data vandaan halen? Bijvoorbeeld
  ledenadministratie, CBS, survey onder leden, gemeenterapport. **In te
  vullen tijdens overleg.**
- **Frequentie**: hoe vaak is de data beschikbaar? Jaarlijks, per kwartaal,
  eenmalig. **In te vullen tijdens overleg.**
- **Eigenaar**: wie binnen de KNSB of daarbuiten is verantwoordelijk voor
  deze bron? **In te vullen tijdens overleg.**

### De tabel

| Prio | ID | Label | Domein | Niveau | KNSB kan sturen | Sliders | Edges in/uit | Datatype (kw/qu) | Mogelijke bron | Frequentie | Eigenaar |
|------|----|-------|--------|--------|-----------------|---------|--------------|------------------|----------------|------------|----------|
| A1 | N002 | Feitelijke deelname | Uitkomsten | L0 | geen | - | 11/2 |  |  |  |  |
| A1 | N003 | Continuïteit | Uitkomsten | L0 | geen | S08 | 12/0 |  |  |  |  |
| A1 | N057 | Recreatieve participatie | Uitkomsten | L0 | geen | S08 | 8/0 |  |  |  |  |
| A1 | N001 | Toelaatbaarheid | Uitkomsten | L0 | geen | - | 4/1 |  |  |  |  |
| A1 | N008 | Kwalificatiestatus | Regels & Administratie | L2 | hoog | S03 | 2/1 |  |  |  |  |
| A1 | N006 | Licentiekosten | Regels & Administratie | L2 | hoog | S03 | 1/1 |  |  |  |  |
| A1 | N007 | Categorie-indeling | Regels & Administratie | L2 | hoog | S03 | 1/1 |  |  |  |  |
| A1 | N005 | Lidmaatschapseis | Regels & Administratie | L2 | hoog | S03 | 0/1 |  |  |  |  |
| A1 | N009 | Inschrijfprocedure | Regels & Administratie | L2 | hoog | S03 | 0/1 |  |  |  |  |
| A1 | N041 | Wedstrijdformat | Organisatie & Aanbod | L2 | hoog | S05 | 0/1 |  |  |  |  |
| A1 | N042 | Selectiesystematiek | Organisatie & Aanbod | L2 | hoog | S08 | 0/1 |  |  |  |  |
| A1 | N043 | Digitale systemen | Organisatie & Aanbod | L2 | hoog | S05 | 0/1 |  |  |  |  |
| A2 | N018 | Intrinsieke motivatie | Psychologisch | L1 | midden | S01 | 13/3 |  |  |  |  |
| A2 | N020 | Zelfeffectiviteit | Psychologisch | L1 | midden | S02, S07 | 4/3 |  |  |  |  |
| A2 | N029 | Financiële draagkracht | Middelen & Logistiek | L1 | geen | S07 | 2/4 |  |  |  |  |
| A2 | N030 | Tijd beschikbaar | Middelen & Logistiek | L1 | geen | S04 | 1/3 |  |  |  |  |
| A2 | N010 | Inschrijfbekwaamheid | Regels & Administratie | L1/L2 | midden | S03, S08 | 3/1 |  |  |  |  |
| A2 | N027 | Clubklimaat | Sociaal | L2 | midden | S06 | 1/4 |  |  |  |  |
| A2 | N036 | IJsbaanbeschikbaarheid | Organisatie & Aanbod | L2 | midden | S04 | 3/2 |  |  |  |  |
| A2 | N039 | Coachkwaliteit | Organisatie & Aanbod | L2 | hoog | - | 0/4 |  |  |  |  |
| A2 | N059 | Openingstijden publiek schaatsen | Organisatie & Aanbod | L2 | midden | S02, S07 | 3/1 |  |  |  |  |
| A2 | N068 | Spelregels & veiligheidsregels | Regels & Administratie | L2 | hoog | - | 0/4 |  |  |  |  |
| A2 | N004 | Licentiestatus | Regels & Administratie | L2 | hoog | - | 2/1 |  |  |  |  |
| A2 | N065 | Herintrede-programma's | Organisatie & Aanbod | L2 | hoog | - | 2/1 |  |  |  |  |
| A2 | N038 | Coachcapaciteit | Organisatie & Aanbod | L2 | hoog | - | 1/1 |  |  |  |  |
| A2 | N067 | Hybride event-beschikbaarheid | Organisatie & Aanbod | L2 | hoog | - | 0/2 |  |  |  |  |
| A2 | N035 | Transponderregistratie | Middelen & Logistiek | L2 | hoog | - | 0/1 |  |  |  |  |
| A2 | N040 | Wedstrijdkalender | Organisatie & Aanbod | L2 | hoog | - | 0/1 |  |  |  |  |
| A2 | N069 | Institutionele prioriteitstelling | Macro-context | L3 | hoog | - | 0/4 |  |  |  |  |
| A3 | N023 | Emotieregulatie | Psychologisch | L1 | midden | S02 | 1/1 |  |  |  |  |
| A3 | N031 | Materiaaltoegang | Middelen & Logistiek | L1 | midden | S04 | 1/1 |  |  |  |  |
| A3 | N032 | Materiaalkosten | Middelen & Logistiek | L1 | midden | S04 | 1/1 |  |  |  |  |
| A3 | N033 | Reisafstand | Middelen & Logistiek | L1 | laag | S04 | 1/1 |  |  |  |  |
| A3 | N062 | Informele sociale groepen | Sociaal | L1 | laag | S05 | 0/2 |  |  |  |  |
| A3 | N021 | Wedstrijdvertrouwen | Psychologisch | L1 | midden | S02 | 0/1 |  |  |  |  |
| A3 | N044 | Verenigingsondersteuning | Organisatie & Aanbod | L2 | midden | S05 | 0/2 |  |  |  |  |
| A3 | N046 | Klimaattrends | Macro-context | L3 | geen | S06 | 0/2 |  |  |  |  |
| A3 | N045 | Economisch klimaat | Macro-context | L3 | geen | S06 | 0/1 |  |  |  |  |
| A3 | N048 | Mediaprofilering | Macro-context | L3 | laag | S01 | 0/1 |  |  |  |  |
| A3 | N049 | Nationale successen | Macro-context | L3 | laag | S06 | 0/1 |  |  |  |  |
| A3 | N050 | Sportvoorkeuren jeugd | Macro-context | L3 | geen | S07 | 0/1 |  |  |  |  |
| A3 | N051 | Duurzaamheidsdiscours | Macro-context | L3 | geen | S01 | 0/1 |  |  |  |  |
| B | N011 | Trainingsvolume | Training & Prestatie | L1 | laag | - | 9/1 |  |  |  |  |
| B | N016 | Prestatieniveau | Training & Prestatie | L1 | laag | - | 5/2 |  |  |  |  |
| B | N015 | Blessuregevoeligheid | Training & Prestatie | L1 | midden | - | 3/3 |  |  |  |  |
| B | N026 | Peergroep/teamgenoten | Sociaal | L1 | midden | - | 1/3 |  |  |  |  |
| B | N012 | Trainingskwaliteit | Training & Prestatie | L1 | midden | - | 2/1 |  |  |  |  |
| B | N019 | Extrinsieke motivatie | Psychologisch | L1 | midden | - | 2/1 |  |  |  |  |
| B | N022 | Ervaren wedstrijdspanning | Psychologisch | L1 | midden | - | 1/2 |  |  |  |  |
| B | N013 | Technisch niveau | Training & Prestatie | L1 | midden | - | 0/2 |  |  |  |  |
| B | N063 | Kwaliteit vroege sportervaring | Psychologisch | L1 | midden | - | 0/1 |  |  |  |  |
| B | N064 | Post-carrière identiteit | Psychologisch | L1 | midden | - | 0/1 |  |  |  |  |
| B | N028 | Coach-atleet relatie | Sociaal | L1/L2 | midden | - | 1/2 |  |  |  |  |
| B | N056 | Seizoenscompensatie | Discipline-specifiek | L1/L2 | midden | - | 1/2 |  |  |  |  |
| B | N058 | Toegangskosten recreatief | Middelen & Logistiek | L1/L2 | midden | - | 1/1 |  |  |  |  |
| B | N052 | Ploegenstructuur | Discipline-specifiek | L2 | midden | - | 1/2 |  |  |  |  |
| B | N037 | IJsuurverdeling | Organisatie & Aanbod | L2 | midden | - | 1/1 |  |  |  |  |
| B | N061 | Participatieflexibiliteit | Organisatie & Aanbod | L2 | midden | - | 1/1 |  |  |  |  |
| B | N053 | Internationale oriëntatie | Discipline-specifiek | L2 | midden | - | 0/1 |  |  |  |  |
| C | N024 | Doeloriëntatie | Psychologisch | L1 | laag | - | 0/3 |  |  |  |  |
| C | N025 | Ouderondersteuning | Sociaal | L1 | laag | - | 0/3 |  |  |  |  |
| C | N034 | Reiskosten | Middelen & Logistiek | L1 | laag | - | 2/1 |  |  |  |  |
| C | N014 | Fysieke capaciteit | Training & Prestatie | L1 | laag | - | 0/2 |  |  |  |  |
| C | N017 | Herstelcapaciteit | Training & Prestatie | L1 | laag | - | 0/2 |  |  |  |  |
| C | N054 | Tactische complexiteit | Discipline-specifiek | L1 | laag | - | 1/1 |  |  |  |  |
| C | N060 | Autonomie / Zelfbepaling | Psychologisch | L1 | laag | - | 0/2 |  |  |  |  |
| C | N066 | Niet-participatie fase | Psychologisch | L1 | geen | - | 0/1 |  |  |  |  |
| C | N047 | Energieprijzen | Macro-context | L3 | geen | - | 0/4 |  |  |  |  |
| C | N055 | Wegveiligheid | Discipline-specifiek | L3 | geen | - | 0/1 |  |  |  |  |

**Samenvatting**: 12 nodes in A1, 17 in A2, 13 in A3, 17 in B, 10 in C.

### Tweede as: data-toegankelijkheid

Naast strategische zwaarte speelt **hoe makkelijk de data te krijgen is**
een rol. Dat is een aparte vraag, want een zeer belangrijke node (A1) kan
duur zijn om te meten, en een minder belangrijke node (A3) kan toevallig
al klaar liggen.

We stellen voor om per ingevulde rij ook één van drie kosten-indicaties
te geven:

- **goedkoop** — al aanwezig in een KNSB-systeem of publiek beschikbaar
  (CBS, KNMI). Voorbeeld: licentiestatus, economisch klimaat.
- **middel** — structureel uit te halen maar vraagt eenmalige inrichting.
  Voorbeeld: IJsbaanbeschikbaarheid via afspraken met baanexploitanten.
- **duur** — vraagt een survey, interview of nieuwe meetmethode.
  Voorbeeld: intrinsieke motivatie, clubklimaat.

Combineren we de twee assen dan ontstaan vier hoeken:

| Strategisch belang | Data-kosten | Actie                                   |
|--------------------|-------------|-----------------------------------------|
| Hoog (A1/A2)       | Goedkoop    | **Quick wins** — meteen oppakken        |
| Hoog (A1/A2)       | Duur        | **Strategische investering** — plannen  |
| Lager (A3/B)       | Goedkoop    | **Meeneemwerk** — als we toch bezig zijn|
| Lager (A3/B/C)     | Duur        | **Uitstellen of literatuur houden**     |

Opvallend voor dit model:

- Alle 8 Regels & Administratie-nodes in A1/A2 zijn waarschijnlijk quick
  wins — dit is KNSB-interne data.
- De Macro-context-nodes in A3 zijn bijna allemaal quick wins via CBS.
- De Psychologisch-nodes in A2 (Intrinsieke motivatie, Zelfeffectiviteit)
  zijn duur maar strategisch — kandidaten voor een geplande survey.

---

## 4. Omgaan met onvolledige koppeling: drie-tier aanpak

Niet elke node krijgt een datastroom. Dat is geen probleem als we eerlijk
zijn over wat we wel en niet weten. Voorstel: we geven elke node en elke
edge één van drie labels.

| Label             | Betekenis                                                                                        | Voorbeeld                                     |
|-------------------|--------------------------------------------------------------------------------------------------|-----------------------------------------------|
| **data-backed**   | We meten deze factor direct, met eigen of externe data.                                          | Licentiestatus uit de ledenadministratie.     |
| **proxy-backed**  | We meten niet de factor zelf, maar een indicator die er dicht bij zit.                           | Clubklimaat gemeten via ledentevredenheid.    |
| **literature-only** | We hebben alleen wetenschappelijke bronnen, geen eigen meting.                                  | Intrinsieke motivatie, tenzij we surveys doen.|

**Waarom is dit nuttig?**

- De gebruiker van de app ziet meteen hoe zeker een uitkomst is.
- We voorkomen dat cijfers uit de simulatie te zeker lijken.
- Het model blijft bruikbaar, ook als maar een deel is gekoppeld.

**In de app** laten we dit terugkomen via een kleurtint in de graaf-viewer
(donker = data-backed, lichter = proxy, grijs = alleen literatuur). Ook
bij elk AI-antwoord vermelden we op welk tier de redenering rust.

---

## 5. Kalibratiedekking per beleidsvraag

Naast labels per node stellen we een **dekkingsmetriek** voor:

> "Voor een gegeven beleidsvraag (bijvoorbeeld: wat is het effect van
> slider S02 Accommodatietoegang op N002 Feitelijke deelname?), tel het
> aantal edges op het pad dat data-backed is, gedeeld door het totaal."

Dat levert een getal tussen 0 en 1. Voorbeeld: "Deze simulatie heeft een
kalibratiedekking van 0.43 — drie van zeven stappen zijn met data
onderbouwd." Dat is een eerlijk signaal aan de beleidsmedewerker.

---

## 6. Techniek: hebben we Neo4j (graafdatabase) nodig?

**Korte versie: nee, nu niet. PostgreSQL is genoeg.**

### Wat is Neo4j?

Neo4j is een database die speciaal gebouwd is voor grafen. Het is krachtig
als je miljoenen verbindingen hebt of als niet-technische mensen
zelfstandig de graaf willen bevragen met een eigen zoektaal (Cypher).

### Wat hebben we nu?

- **Graafstructuur**: in een JSON-bestand (`sportdeelname_graph.json`).
  De app laadt dit met NetworkX, een Python-bibliotheek. Dat is razendsnel
  voor 69 nodes — een graaf van deze omvang past ruim in het geheugen.
- **Geen database voor data-koppeling**: die moeten we wel opzetten.

### Wat stellen we voor?

Twee simpele tabellen naast het bestaande JSON-model, in PostgreSQL (die
staat al op de roadmap voor productie):

1. **`node_observation`** — metingen per node over tijd
   - `node_id`, `timestamp`, `value`, `source`, `confidence`
2. **`edge_calibration`** — resultaten van de kalibratie per edge
   - `edge_id`, `fitted_params`, `r2`, `n_obs`, `fit_date`

Dit dekt ongeveer 95% van de behoefte. Voordelen:

- **Geen extra systeem** — PostgreSQL is er al.
- **Eenvoudig in onderhoud** — iedere data-analist kent SQL.
- **Kost geen licentiegeld** — Neo4j heeft een betaalde variant voor productie.

### Wanneer wél Neo4j?

Pas overwegen als één van deze situaties zich voordoet:

- We gaan meerdere modellen samenvoegen (schaatsen + wielrennen + …).
- We groeien naar meer dan ~1000 nodes.
- Niet-technische gebruikers moeten zelf ad-hoc vragen kunnen stellen aan
  de graaf met een eigen query-taal.

Voor nu: **NetworkX + JSON voor de graaf, PostgreSQL voor de data.**

---

## 7. Hoe verhoudt dit zich tot het data warehouse van de KNSB?

De KNSB werkt toe naar een eigen **data warehouse (DWH)**: één centrale
plek waar operationele data (ledenadministratie, licenties, wedstrijden,
financiën, etc.) bij elkaar komt, klaar voor analyse en rapportage. Dat
is goed nieuws voor dit project — mits we de rollen helder scheiden.

### Wat is een data warehouse, in het kort

Een DWH is een gestructureerde database waar data uit verschillende
bronsystemen (Ledencentraal, transponder-administratie, financiële
pakketten, enzovoort) periodiek naartoe wordt gekopieerd en gestandaardiseerd.
Daardoor kan je analyses over alle systemen heen doen, met consistente
definities. Typische bouwstenen:

- **Bronlagen** (raw / staging): ruwe kopieën van bronsystemen.
- **Gestandaardiseerde laag** (core / integrated): ontdubbelde, gekoppelde
  feiten en dimensies.
- **Data marts**: thematische uitsnedes, afgestemd op een bepaalde
  gebruiksgroep (bijv. "ledenmart" of "wedstrijdmart").

### Hoe past onze graaf-datakoppeling erbij?

De graaf-app is een **afnemer (consumer)** van het DWH, geen
concurrentie. Onze `node_observation`-tabel zou idealiter geen directe
kopie van bronsystemen zijn, maar een **data mart op het DWH**:

```
┌──────────────────────┐
│ Bronsystemen KNSB    │  ledenadm, licenties, wedstrijden, …
└─────────┬────────────┘
          │ ETL/ELT
┌─────────▼────────────┐
│ Data warehouse       │  core-laag, dimensies & feiten
└─────────┬────────────┘
          │ view of extract
┌─────────▼────────────┐
│ Graaf-data-mart      │  node_observation, edge_calibration
│ (onze PostgreSQL)    │
└─────────┬────────────┘
          │
┌─────────▼────────────┐
│ Graaf Zeppelin app   │  NetworkX + JSON + koppeling aan mart
└──────────────────────┘
```

### Wat betekent dit concreet?

1. **Onze node-audit wordt data-vraag voor het DWH**. De ingevulde tabel
   in hoofdstuk 3 vormt feitelijk een inventarisatie: "welke metingen
   willen wij periodiek uit het DWH hebben?" Dit is een bekende,
   eenduidige deliverable voor een DWH-traject. In DWH-termen: wij leveren
   een lijst van benodigde **meetpunten (facts)** en hun
   **dimensies** (tijd, club, discipline, categorie).

2. **Alignment op definities is cruciaal**. Een node als "Feitelijke
   deelname" moet in het DWH dezelfde operationele definitie krijgen
   (bijvoorbeeld: hoeveel leden minstens X wedstrijden hebben gereden per
   jaar). Dit is precies waar DWH-trajecten hun waarde bewijzen — het
   forceert een gemeenschappelijke taal.

3. **We blokkeren niet op het DWH**. DWH-trajecten duren doorgaans lang.
   Wij beginnen met A1-nodes die óók *zonder* DWH uit bronsystemen
   beschikbaar zijn (bijvoorbeeld een directe extract uit de
   ledenadministratie), en migreren dat later naar DWH-views zodra die er
   zijn. Onze `node_observation`-tabel blijft hetzelfde; alleen de bron
   verschuift.

4. **Kwalitatieve data past er niet klassiek in**. DWH's zijn gebouwd
   voor gestructureerde feiten. Survey-data (bijvoorbeeld over motivatie
   of clubklimaat) kan wel in het DWH als we scores en antwoorden als
   feitenrijen modelleren, maar open tekst en kwalitatieve interviews
   horen eerder in een apart *data lake* of een documentstore. Aandachtspunt
   om vroeg te agenderen met de DWH-architecten.

5. **Kans: governance en eigenaarschap**. Een DWH-traject regelt vaak ook
   data-eigenaarschap en kwaliteitsafspraken. Dat is precies wat wij nodig
   hebben voor de kolom "Eigenaar" in de audit-tabel. Koppel onze
   node-audit aan het DWH-data-catalogusproces — dan lift ons model mee op
   hun governance.

### Betekent dit een andere techniekkeuze?

Nee, niet fundamenteel. Onze keuzes blijven:

- **Graafstructuur** → NetworkX + JSON (onveranderd, beheerd binnen het
  modelproject).
- **Observaties** → PostgreSQL-tabellen die *gevoed* worden door het DWH
  (via scheduled extract, een view of een directe query).
- **Kalibratie-resultaten** → PostgreSQL (eigen artefact, geen DWH-data).

Eventueel kan de graaf-data-mart later in het DWH zelf landen in plaats
van in een aparte PostgreSQL, maar dat is een uitvoeringsdetail voor
later. Het versnelt niets om dat nu al te forceren.

### Samengevat

Het DWH en onze graaf versterken elkaar: de graaf geeft het DWH een
**concreet, model-gedreven doel** (welke feiten moeten er uit?) en het
DWH levert ons een **stabiele, gestandaardiseerde bron**. Het DWH is geen
vervanger van de graaf en andersom ook niet — ze zitten in verschillende
lagen van dezelfde stapel.

---

## 8. Dekkingsdiagram (te maken ná het overleg)

Zodra de node-audit tabel (hoofdstuk 3) is ingevuld, maken we een
visualisatie van de graaf waarbij elke node één van drie kleuren krijgt:

- Donker = data-backed
- Halftint = proxy-backed
- Licht = literature-only

Hiermee zie je in één oogopslag waar de "donkere vlekken" (witte plekken)
zitten. Dit kunnen we direct in de bestaande D3-viewer van de app
implementeren.

---

## 9. Beslispunten voor het overleg

Om het gesprek niet te breed te laten worden, stellen we voor om te
eindigen met een klein aantal besluiten:

1. **Akkoord op de hybride aanpak**: literatuur blijft de basis, data
   verbetert waar mogelijk. We gooien het literatuur-werk niet weg.
2. **Akkoord op de drie-tier labeling**: elke node en edge krijgt een
   tier (data / proxy / literatuur) en die is zichtbaar in de app.
3. **Akkoord op A1 als startscope**: we beginnen met de 12 A1-nodes,
   niet met alle 42 uit A.
4. **Akkoord op de techniekkeuze**: PostgreSQL naast het bestaande
   NetworkX/JSON-model. Neo4j pas als er een concrete aanleiding komt.
5. **Akkoord op DWH-koppeling als doelplaatje**: de graaf-app wordt
   afnemer van het DWH; onze audit-tabel leveren we aan als data-vraag
   voor het DWH-traject.

Optioneel vervolgpunt:

6. **Scope MVP**: kies 1 of 2 concrete beleidsvragen (zie
   `example_questions` in de metadata van het model) waarop we als eerste
   álle nodes op het pad volledig koppelen. Zo hebben we snel een
   overtuigende demo in plaats van lang te moeten wachten op volledige
   dekking.

---

## Bijlage: telling per domein en prioriteit

| Domein                   | A1 | A2 | A3 | B | C | Totaal |
|--------------------------|----|----|----|---|---|--------|
| Uitkomsten               | 4  | 0  | 0  | 0 | 0 | 4      |
| Regels & Administratie   | 5  | 3  | 0  | 0 | 0 | 8      |
| Organisatie & Aanbod     | 3  | 7  | 1  | 2 | 0 |13      |
| Middelen & Logistiek     | 0  | 3  | 3  | 1 | 1 | 8      |
| Psychologisch            | 0  | 2  | 2  | 4 | 3 |11      |
| Sociaal                  | 0  | 1  | 1  | 2 | 1 | 5      |
| Macro-context            | 0  | 1  | 6  | 0 | 1 | 8      |
| Training & Prestatie     | 0  | 0  | 0  | 5 | 2 | 7      |
| Discipline-specifiek     | 0  | 0  | 0  | 3 | 2 | 5      |
| **Totaal**               |**12**|**17**|**13**|**17**|**10**|**69**|
