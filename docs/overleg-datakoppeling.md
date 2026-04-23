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

- **Prio**: voorgestelde prioriteit voor datakoppeling.
  - **A** = hoge prioriteit. Raakt een uitkomst (L0), of de KNSB kan er
    direct op sturen, of hangt aan een beleidsslider.
  - **B** = middelhoog. Belangrijk tussenstation, vaak veel verbindingen.
  - **C** = lage prioriteit. Perifeer, weinig invloed, of moeilijk
    meetbaar. Kan later of via literatuur.
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
| A | N002 | Feitelijke deelname | Uitkomsten | L0 | geen | - | 11/2 |  |  |  |  |
| A | N003 | Continuïteit | Uitkomsten | L0 | geen | S08 | 12/0 |  |  |  |  |
| A | N057 | Recreatieve participatie | Uitkomsten | L0 | geen | S08 | 8/0 |  |  |  |  |
| A | N001 | Toelaatbaarheid | Uitkomsten | L0 | geen | - | 4/1 |  |  |  |  |
| A | N018 | Intrinsieke motivatie | Psychologisch | L1 | midden | S01 | 13/3 |  |  |  |  |
| A | N020 | Zelfeffectiviteit | Psychologisch | L1 | midden | S02, S07 | 4/3 |  |  |  |  |
| A | N029 | Financiële draagkracht | Middelen & Logistiek | L1 | geen | S07 | 2/4 |  |  |  |  |
| A | N030 | Tijd beschikbaar | Middelen & Logistiek | L1 | geen | S04 | 1/3 |  |  |  |  |
| A | N023 | Emotieregulatie | Psychologisch | L1 | midden | S02 | 1/1 |  |  |  |  |
| A | N031 | Materiaaltoegang | Middelen & Logistiek | L1 | midden | S04 | 1/1 |  |  |  |  |
| A | N032 | Materiaalkosten | Middelen & Logistiek | L1 | midden | S04 | 1/1 |  |  |  |  |
| A | N033 | Reisafstand | Middelen & Logistiek | L1 | laag | S04 | 1/1 |  |  |  |  |
| A | N062 | Informele sociale groepen | Sociaal | L1 | laag | S05 | 0/2 |  |  |  |  |
| A | N021 | Wedstrijdvertrouwen | Psychologisch | L1 | midden | S02 | 0/1 |  |  |  |  |
| A | N010 | Inschrijfbekwaamheid | Regels & Administratie | L1/L2 | midden | S03, S08 | 3/1 |  |  |  |  |
| A | N027 | Clubklimaat | Sociaal | L2 | midden | S06 | 1/4 |  |  |  |  |
| A | N036 | IJsbaanbeschikbaarheid | Organisatie & Aanbod | L2 | midden | S04 | 3/2 |  |  |  |  |
| A | N039 | Coachkwaliteit | Organisatie & Aanbod | L2 | hoog | - | 0/4 |  |  |  |  |
| A | N059 | Openingstijden publiek schaatsen | Organisatie & Aanbod | L2 | midden | S02, S07 | 3/1 |  |  |  |  |
| A | N068 | Spelregels & veiligheidsregels | Regels & Administratie | L2 | hoog | - | 0/4 |  |  |  |  |
| A | N004 | Licentiestatus | Regels & Administratie | L2 | hoog | - | 2/1 |  |  |  |  |
| A | N008 | Kwalificatiestatus | Regels & Administratie | L2 | hoog | S03 | 2/1 |  |  |  |  |
| A | N065 | Herintrede-programma's | Organisatie & Aanbod | L2 | hoog | - | 2/1 |  |  |  |  |
| A | N006 | Licentiekosten | Regels & Administratie | L2 | hoog | S03 | 1/1 |  |  |  |  |
| A | N007 | Categorie-indeling | Regels & Administratie | L2 | hoog | S03 | 1/1 |  |  |  |  |
| A | N038 | Coachcapaciteit | Organisatie & Aanbod | L2 | hoog | - | 1/1 |  |  |  |  |
| A | N044 | Verenigingsondersteuning | Organisatie & Aanbod | L2 | midden | S05 | 0/2 |  |  |  |  |
| A | N067 | Hybride event-beschikbaarheid | Organisatie & Aanbod | L2 | hoog | - | 0/2 |  |  |  |  |
| A | N005 | Lidmaatschapseis | Regels & Administratie | L2 | hoog | S03 | 0/1 |  |  |  |  |
| A | N009 | Inschrijfprocedure | Regels & Administratie | L2 | hoog | S03 | 0/1 |  |  |  |  |
| A | N035 | Transponderregistratie | Middelen & Logistiek | L2 | hoog | - | 0/1 |  |  |  |  |
| A | N040 | Wedstrijdkalender | Organisatie & Aanbod | L2 | hoog | - | 0/1 |  |  |  |  |
| A | N041 | Wedstrijdformat | Organisatie & Aanbod | L2 | hoog | S05 | 0/1 |  |  |  |  |
| A | N042 | Selectiesystematiek | Organisatie & Aanbod | L2 | hoog | S08 | 0/1 |  |  |  |  |
| A | N043 | Digitale systemen | Organisatie & Aanbod | L2 | hoog | S05 | 0/1 |  |  |  |  |
| A | N069 | Institutionele prioriteitstelling | Macro-context | L3 | hoog | - | 0/4 |  |  |  |  |
| A | N046 | Klimaattrends | Macro-context | L3 | geen | S06 | 0/2 |  |  |  |  |
| A | N045 | Economisch klimaat | Macro-context | L3 | geen | S06 | 0/1 |  |  |  |  |
| A | N048 | Mediaprofilering | Macro-context | L3 | laag | S01 | 0/1 |  |  |  |  |
| A | N049 | Nationale successen | Macro-context | L3 | laag | S06 | 0/1 |  |  |  |  |
| A | N050 | Sportvoorkeuren jeugd | Macro-context | L3 | geen | S07 | 0/1 |  |  |  |  |
| A | N051 | Duurzaamheidsdiscours | Macro-context | L3 | geen | S01 | 0/1 |  |  |  |  |
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

**Samenvatting**: 42 nodes in prio A, 17 in prio B, 10 in prio C.

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

## 7. Dekkingsdiagram (te maken ná het overleg)

Zodra de node-audit tabel (hoofdstuk 3) is ingevuld, maken we een
visualisatie van de graaf waarbij elke node één van drie kleuren krijgt:

- Donker = data-backed
- Halftint = proxy-backed
- Licht = literature-only

Hiermee zie je in één oogopslag waar de "donkere vlekken" (witte plekken)
zitten. Dit kunnen we direct in de bestaande D3-viewer van de app
implementeren.

---

## 8. Drie beslispunten voor het overleg

Om het gesprek niet te breed te laten worden, stellen we voor om te
eindigen met drie besluiten:

1. **Akkoord op de hybride aanpak**: literatuur blijft de basis, data
   verbetert waar mogelijk. We gooien het literatuur-werk niet weg.
2. **Akkoord op de drie-tier labeling**: elke node en edge krijgt een
   tier (data / proxy / literatuur) en die is zichtbaar in de app.
3. **Akkoord op de techniekkeuze**: PostgreSQL naast het bestaande
   NetworkX/JSON-model. Neo4j pas als er een concrete aanleiding komt.

Optioneel vierde punt:

4. **Scope MVP**: kies 1 of 2 concrete beleidsvragen (zie
   `example_questions` in de metadata van het model) waarop we als eerste
   álle nodes op het pad volledig koppelen. Zo hebben we snel een
   overtuigende demo in plaats van lang te moeten wachten op volledige
   dekking.

---

## Bijlage: telling per domein en prioriteit

| Domein                   | A | B | C | Totaal |
|--------------------------|---|---|---|--------|
| Uitkomsten               | 4 | 0 | 0 | 4      |
| Regels & Administratie   | 8 | 0 | 0 | 8      |
| Organisatie & Aanbod     |11 | 2 | 0 |13      |
| Middelen & Logistiek     | 6 | 1 | 1 | 8      |
| Psychologisch            | 4 | 4 | 3 |11      |
| Sociaal                  | 2 | 2 | 1 | 5      |
| Macro-context            | 7 | 0 | 1 | 8      |
| Training & Prestatie     | 0 | 5 | 2 | 7      |
| Discipline-specifiek     | 0 | 3 | 2 | 5      |
| **Totaal**               |**42**|**17**|**10**|**69**|
