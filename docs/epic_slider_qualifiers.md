# EPIC: Slider Kwalificatievragen — contextbepaling voor beleidssimulaties

## Doel

Elke beleidsslider in het sportdeelnamemodel voorzien van gevalideerde kwalificerende vragen, zodat een LLM-agent (Copilot, GPT, Claude) op basis van gebruikersantwoorden automatisch de juiste sliderwaarde kan bepalen — zonder dat de gebruiker technische kennis nodig heeft van het causale model.

## Waarom

- Sliders hebben abstracte waarden (0–1) die voor eindgebruikers niets betekenen
- Een agent die "zet prestatiecultuur op 0.7" vraagt is onbruikbaar
- Kwalificerende vragen vertalen de context van een organisatie naar sliderwaarden
- Door dit in de **data** op te slaan (niet in de prompt) is het reproduceerbaar en vergelijkbaar tussen organisaties
- Relevantiefiltering voorkomt dat gebruikers bij elke vraag alle 16+ vragen moeten beantwoorden

## Huidige status

De technische infrastructuur is gebouwd:
- `qualifiers` veld toegevoegd aan alle 8 sliders in het graph-schema
- API endpoints: `GET /sliders/{id}/qualify`, `GET /sliders/qualify/relevant`, `POST /sliders/qualify`
- Relevantiefiltering op basis van `related_nodes` en `primary_clusters`

**Wat nu nodig is:** inhoudelijke validatie en verbetering van de vragen zelf.

---

## Stories

### Story 1: Inhoudelijke review van kwalificerende vragen per slider

**Als** domeinexpert / onderzoeker
**Wil ik** de huidige kwalificerende vragen per slider beoordelen op inhoudelijke juistheid
**Zodat** de vragen daadwerkelijk de juiste context meten voor elke slider

#### Te reviewen sliders en hun huidige vragen

| Slider | ID | Huidige vragen |
|--------|-----|----------------|
| Economisch klimaat | S01 | Financiële drempel leden + Financiële situatie club |
| Accommodatietoegang | S02 | Beschikbaarheid faciliteiten + Bereikbaarheid locaties |
| Bondsbeleid & regelgeving | S03 | Mate van regelgeving + Licentie/inschrijfprocedures |
| Prestatiecultuur | S04 | Cultuur vereniging + Leeftijd start selectie |
| Clubklimaat & sociale cohesie | S05 | Sfeer vereniging + Inclusiviteit voor nieuwe leden |
| Vrijwilligerscapaciteit | S06 | Vrijwilligerssituatie + Beschikbaarheid trainers |
| Seizoen & klimaat | S07 | Duur sportseizoen + Alternatieve trainingsmogelijkheden |
| Levensfase & transitie | S08 | Leeftijdsgroep + Stabiliteit levensfase |

#### Acceptatiecriteria

- [ ] Elke vraag is getoetst aan het wetenschappelijk mechanisme beschreven in de slider-definitie
- [ ] De antwoordopties dekken het volledige spectrum (0–1) zonder gaten of overlap
- [ ] De mapping van antwoord naar waarde is onderbouwd (waarom is "mix van plezier en presteren" = 0.5?)
- [ ] Vragen zijn begrijpelijk voor niet-technische gebruikers (sportbondmedewerkers, clubbestuurders)
- [ ] Vragen zijn cultuur- en discipline-neutraal (niet alleen voor schaatsen)

---

### Story 2: Validatie van waarde-mappings met empirische data

**Als** onderzoeker
**Wil ik** de mapping van antwoorden naar numerieke waarden valideren
**Zodat** de sliderwaarden daadwerkelijk het juiste effect produceren in de simulatie

#### Acceptatiecriteria

- [ ] Per slider: test of de waarden uit de kwalificatievragen, wanneer ingevoerd in de simulatie, plausibele resultaten opleveren
- [ ] Vergelijk: werkt de simulatie met gekwalificeerde waarden beter dan met de defaults (0.5)?
- [ ] Controleer of de gemiddelde waarde van meerdere antwoorden (de huidige aggregatiemethode) de juiste benadering is — of is gewogen middelen of een ander algoritme beter?
- [ ] Documenteer eventuele niet-lineaire relaties die de simpele middeling vertekenen

---

### Story 3: Uitbreiding met discipline-specifieke vragen

**Als** domeinexpert
**Wil ik** onderzoeken of sommige sliders discipline-specifieke kwalificatievragen nodig hebben
**Zodat** de vragen relevanter zijn voor verschillende sportcontexten

#### Acceptatiecriteria

- [ ] Identificeer welke sliders discipline-specifieke nuances vereisen (bijv. seizoenslengte verschilt sterk per sport)
- [ ] Ontwerp varianten van kwalificatievragen per discipline-categorie (binnensport vs. buitensport, team vs. individueel)
- [ ] Bepaal of dit via een `discipline` filter in de API moet, of via aparte vragensets
- [ ] Lever aangepaste vragen op in hetzelfde JSON-formaat

---

### Story 4: Optimalisatie van de relevantiefiltering

**Als** onderzoeker
**Wil ik** valideren of de huidige relevantiefiltering (via `related_nodes` en `primary_clusters`) de juiste sliders selecteert
**Zodat** gebruikers niet te veel en niet te weinig vragen krijgen

#### Acceptatiecriteria

- [ ] Test met 10+ realistische gebruikersvragen of de juiste sliders worden geselecteerd
- [ ] Identificeer edge cases: vragen waarbij relevante sliders worden gemist of irrelevante worden meegenomen
- [ ] Bepaal of aanvullende filteringscriteria nodig zijn (bijv. op basis van `sensitivity_key` in de edges)
- [ ] Documenteer de bevindingen en eventuele aanpassingen aan het filteralgoritme

---

### Story 5: Gebruikerstest met sportbondmedewerkers

**Als** productowner
**Wil ik** de kwalificatievragen testen met echte eindgebruikers
**Zodat** we weten of de vragen begrijpelijk en bruikbaar zijn in de praktijk

#### Acceptatiecriteria

- [ ] Minimaal 5 testgebruikers (sportbondmedewerkers / clubbestuurders)
- [ ] Elke gebruiker beantwoordt de kwalificatievragen voor hun eigen context
- [ ] Meting: hoelang duurt het invullen? Zijn de vragen duidelijk? Herkennen ze hun organisatie in de antwoorden?
- [ ] Vergelijk: komen de gesimuleerde resultaten overeen met hun verwachtingen?
- [ ] Feedback verzamelen en verwerken in verbeterde vraagformuleringen

---

## Technische context

### API Endpoints

```
GET  /api/graph/sliders/{id}/qualify      → Vragen voor één slider
GET  /api/graph/sliders/qualify/relevant?factor_ids=N018,N033  → Alleen relevante vragen
POST /api/graph/sliders/qualify           → Antwoorden → sliderwaarden
POST /api/graph/simulate                  → Sliderwaarden → effecten
```

### Agent-flow (beoogd)

```
Gebruiker: "Wat gebeurt er als we meer investeren in coaching?"
    ↓
Agent: bepaalt relevante factoren (N045, N046, N027)
    ↓
Agent: GET /sliders/qualify/relevant?factor_ids=N045,N046,N027
    → Krijgt alleen S05 (clubklimaat) en S06 (vrijwilligers) terug
    ↓
Agent: stelt 4 vragen (2 per relevante slider)
    ↓
Agent: POST /sliders/qualify met antwoorden
    → Krijgt {S05: 0.65, S06: 0.4} terug
    ↓
Agent: POST /simulate met die waarden
    → Geeft gecontextualiseerd antwoord
```

### JSON-formaat kwalificatievragen

```json
{
  "qualifiers": [
    {
      "question": "Hoe zou je de sfeer binnen jullie vereniging omschrijven?",
      "options": [
        {"label": "Warm, iedereen welkom en betrokken", "value": 0.85},
        {"label": "Gezellig, goede onderlinge band", "value": 0.65},
        {"label": "Functioneel, mensen komen voor de sport", "value": 0.4},
        {"label": "Kil, weinig onderling contact", "value": 0.15}
      ]
    }
  ]
}
```

## Definition of Done

- Alle 8 sliders hebben gevalideerde kwalificatievragen
- Waarde-mappings zijn onderbouwd en getest
- Relevantiefiltering is gevalideerd met realistische use cases
- Minimaal één gebruikerstest is uitgevoerd en feedback verwerkt
- Eventuele discipline-specifieke varianten zijn geïdentificeerd
