# Graaf Zeppelin — Het verhaal achter de ontwikkeling

## Wat is Graaf Zeppelin?

Graaf Zeppelin is een online platform dat beleidsmedewerkers helpt om betere beslissingen te nemen. Stel je voor: je werkt bij een sportbond en je wilt weten wat er gebeurt als je investeert in betere sportaccommodaties. Heeft dat effect op het aantal leden? En zo ja, via welke weg? Graaf Zeppelin geeft antwoord op dat soort vragen — niet op basis van onderbuikgevoel, maar op basis van een wetenschappelijk onderbouwd model.

Het platform combineert twee krachtige ideeën: een causaal model dat laat zien hoe factoren met elkaar samenhangen, en kunstmatige intelligentie (AI) die in gewone taal kan uitleggen wat de gevolgen zijn van beleidskeuzes.

---

## Hoofdstuk 1: De basis leggen

### Het causale model begrijpelijk maken (EPIC 1)

Alles begon met het fundament: het causale model. Dit model — een zogenaamde DAG (een soort stroomschema van oorzaak en gevolg) — beschrijft welke factoren elkaar beïnvloeden. Denk aan: "betere coaching leidt tot hogere kwaliteit van het sportaanbod, wat weer leidt tot meer sportdeelname."

De eerste stap was dit model in de computer laden en doorzoekbaar maken. Vervolgens kregen gebruikers een visuele weergave: een interactief diagram waarin je kunt klikken op factoren om te zien welke paden er lopen. Zo wordt een complex wetenschappelijk model ineens toegankelijk voor iedereen.

### Wat als we de knoppen omdraaien? (EPIC 2)

Een model bekijken is één ding, maar ermee spelen is veel krachtiger. Daarom kwamen er schuifbalken — acht stuks, gekoppeld aan beleidsinstrumenten. Door aan een schuifbalk te draaien (bijvoorbeeld "investering in coaching" van laag naar hoog) berekent het systeem automatisch wat het verwachte effect is op alle andere factoren.

Achter de schermen gebruikt het platform drie wiskundige modellen om die berekeningen te doen, zodat de resultaten realistisch zijn. Een kleine investering heeft een ander effect dan een grote — dat wordt netjes meegenomen.

---

## Hoofdstuk 2: De AI-assistent

### Vragen stellen in gewone taal (EPIC 3)

Niet iedereen wil met grafieken en schuifbalken werken. Daarom werd er een AI-assistent ingebouwd. Gebruikers kunnen gewoon typen: "Wat gebeurt er als we investeren in betere coaching?" De AI leest het causale model, zoekt de relevante factoren, en formuleert een onderbouwd antwoord.

Het bijzondere is dat de AI niet zomaar mag verzinnen wat het wil. Het antwoord wordt begrensd door het wetenschappelijke model. Zo combineer je het gemak van een chatgesprek met de betrouwbaarheid van een onderbouwd model.

### Bruikbaar voor iedereen (EPIC 6)

De eerste versie van de AI-assistent werkte, maar was nog niet ideaal voor dagelijks gebruik. Er kwamen voorbeeldvragen zodat gebruikers snel konden starten. Het systeem ging automatisch de juiste factoren selecteren bij een vraag (in plaats van dat de gebruiker ze zelf moest aanvinken). En er kwam een gesprekgeschiedenis, zodat je kon terugbladeren naar eerdere vragen. Als er iets mis ging met de AI — bijvoorbeeld als de achterliggende dienst even niet bereikbaar was — kreeg de gebruiker een duidelijke melding in plaats van een technische foutcode.

---

## Hoofdstuk 3: Toegang en betaalmodel

### Inloggen en licenties (EPIC 4)

Een platform als dit moet weten wie er inlogt. Er kwam een volledig inlogsysteem met registratie, wachtwoorden en sessies. Daarnaast werd er een licentiesysteem gebouwd met drie niveaus: gratis, standaard en premium. Elk niveau heeft zijn eigen mogelijkheden en limieten.

### Een eerlijk verdienmodel (EPIC 7)

Om het platform duurzaam te maken, werd er een doordacht verdienmodel ontworpen. Iedereen kan twee gratis vragen per dag stellen — genoeg om het platform te leren kennen. Wie meer wil, kan kiezen uit betaalde abonnementen. Er is ook een creditssysteem: je betaalt voor wat je gebruikt, niet meer. En voor organisaties die al een eigen AI-abonnement hebben (bij OpenAI of Anthropic), is er de mogelijkheid om je eigen sleutel te koppelen. Zo betaal je alleen voor het platform zelf, niet dubbel voor de AI.

---

## Hoofdstuk 4: De begeleide beleidsverkenning

### Van vraag tot advies (EPIC 5)

Dit is het hart van het platform. Een beleidsmedewerker typt een vraag, bijvoorbeeld: "Hoe kunnen we de sportdeelname onder jongeren verhogen?" Het systeem analyseert de vraag, stelt gerichte vervolgvragen om de situatie beter te begrijpen, en laat de gebruiker vervolgens met schuifbalken aangeven welke interventies hij overweegt.

Het resultaat is een onderbouwd advies met verwachte effecten, visuele grafieken en de mogelijkheid om het rapport te downloaden. Eerdere verkenningen worden opgeslagen, zodat je ze later kunt vergelijken of delen met collega's.

Het dashboard werd aangescherpt met een overzichtelijke startpagina, een stapsgewijze introductie voor nieuwe gebruikers en een helder overzicht van opgeslagen verkenningen.

---

## Hoofdstuk 5: Klaar voor de echte wereld

### Stabiliteit en kwaliteit (EPIC 9)

Voordat een platform de deur uit kan, moet het betrouwbaar zijn. Er werden ruim 200 geautomatiseerde tests geschreven die controleren of alles correct werkt — van het aanmaken van een account tot het uitvoeren van een complete beleidsverkenning. Foutmeldingen werden verbeterd zodat gebruikers altijd begrijpen wat er aan de hand is. En er kwam een uitgebreide handleiding bij het project.

### Klaar voor productie (EPIC 10)

Het platform werd verpakt in een Docker-container: een soort digitale doos die je op elke server kunt neerzetten. De database werd geüpgraded naar PostgreSQL, een professionele database die grote hoeveelheden data aankan. Er kwam ondersteuning voor het exporteren van rapporten en voor het werken met meerdere causale modellen tegelijk.

---

## Hoofdstuk 6: Beveiliging

### Een veilig platform (EPIC 11)

Beveiliging is geen optie, het is een vereiste. Het hele platform werd doorgelicht aan de hand van internationale beveiligingsstandaarden (OWASP Top 10). Dit leidde tot vijf verbeterrondes:

**Sterke inlogbeveiliging.** Wachtwoorden worden nu opgeslagen met bcrypt — een methode die het voor aanvallers vrijwel onmogelijk maakt om wachtwoorden te achterhalen. Er kwamen eisen aan wachtwoordsterkte (minimaal 8 tekens, hoofdletters, cijfers en speciale tekens). En er werd een systeem van verversingstokens ingevoerd, zodat sessies veilig verlengd worden zonder dat je steeds opnieuw hoeft in te loggen.

**Bescherming van de interfaces.** Alle communicatie tussen de browser en het platform wordt gecontroleerd op geldigheid. Er zijn beveiligingskoppen toegevoegd die veelvoorkomende aanvallen blokkeren, zoals het insluiten van het platform in een kwaadaardige website. Externe bronnen worden geverifieerd met digitale vingerafdrukken.

**Toegangscontrole.** Niet elke gebruiker mag alles. Er kwam een rollensysteem (gebruiker, analist, beheerder) zodat gevoelige functies — zoals het wisselen van AI-model of het bijboeken van tegoed — alleen toegankelijk zijn voor bevoegde personen. Gesprekken van de ene gebruiker zijn onzichtbaar voor de andere.

**Logboek en monitoring.** Het platform houdt bij wat er gebeurt, zodat verdachte activiteiten gesignaleerd kunnen worden — zonder dat persoonlijke gegevens worden blootgesteld in foutmeldingen.

**Automatische controles.** Bij elke wijziging aan de software worden automatisch drie beveiligingsscanners uitgevoerd die bekende kwetsbaarheden opsporen. Zo wordt voorkomen dat er per ongeluk een beveiligingslek wordt geïntroduceerd.

---

## Hoofdstuk 7: Klaar voor elk domein

### Multi-domein ondersteuning (EPIC 12)

Tot dit punt was het platform gebouwd rondom één specifiek onderwerp: sportdeelname. Maar de onderliggende technologie is veel breder toepasbaar. Wat als dezelfde software ook gebruikt kan worden voor gezondheidszorg, onderwijs of duurzaamheidsbeleid?

Dat is precies wat er in deze laatste fase is gerealiseerd. Alle verwijzingen naar "sportdeelname" zijn vervangen door dynamische waarden die uit het model zelf komen. De AI-assistent stelt zich voor met de juiste rol en context, afhankelijk van het geladen model. Voorbeeldvragen worden automatisch geladen vanuit het modelbestand. En zelfs de taal van het model (Nederlands of Engels) wordt herkend en correct verwerkt.

Het resultaat: om Graaf Zeppelin in te zetten voor een compleet ander domein, hoef je slechts één bestand te vervangen — het causale model. De software past zich automatisch aan. Geen programmeerwerk nodig.

---

## In cijfers

| Wat | Aantal |
|-----|--------|
| Afgeronde epics | 10 van 12 |
| Afgeronde stories | 48 |
| Geautomatiseerde tests | 214 |
| Beveiligingsstandaarden | OWASP Top 10, CWE/SANS Top 25 |
| Ondersteunde AI-diensten | OpenAI, Anthropic (+ eigen sleutel) |
| Ondersteunde talen in modellen | Nederlands en Engels |

---

## Wat staat er nog op de planning?

Twee onderdelen zijn bewust nog niet opgepakt:

- **Inhoudelijke validatie van kwalificatievragen (EPIC 8)** — De techniek is klaar, maar de inhoudelijke vragen moeten nog worden beoordeeld door domeinexperts en getest met echte beleidsmedewerkers bij sportbonden.
- **Monitoring en logging (S10-03)** — Uitgebreide operationele monitoring voor als het platform op grotere schaal wordt ingezet.

---

## Conclusie

Graaf Zeppelin is in twaalf stappen gegroeid van een technisch prototype naar een compleet, veilig en flexibel platform. Het maakt wetenschappelijk onderbouwd causaal redeneren toegankelijk voor beleidsmedewerkers die geen technische achtergrond nodig hebben. En dankzij de multi-domein architectuur kan dezelfde technologie morgen worden ingezet voor een heel ander beleidsvraagstuk — zonder ook maar één regel code te veranderen.
