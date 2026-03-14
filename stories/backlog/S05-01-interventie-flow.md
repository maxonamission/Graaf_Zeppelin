# S05-01: Begeleide interventie-flow

**Epic:** EPIC-05 Begeleide beleidsverkenning
**Status:** 🔲 Backlog
**Prioriteit:** Hoog

## User Story

**Als** beleidsmedewerker
**Wil ik** een beleidsvraag stellen en begeleid worden naar een onderbouwd advies
**Zodat** ik niet zelf hoef te weten welke factoren en sliders relevant zijn

## Beschrijving

De kern van het product: een workflow die de gebruiker van vraag naar advies leidt.

```
Gebruiker stelt beleidsvraag
    → App bepaalt relevante sliders (via factor-matching)
    → Stelt kwalificatievragen (multiple-choice)
    → Simuleert met gekwalificeerde waarden
    → Toont resultaat met uitleg en onderbouwing
```

## Acceptatiecriteria

- [ ] Gebruiker kan een beleidsvraag formuleren in vrije tekst
- [ ] App selecteert automatisch relevante sliders op basis van de vraag
- [ ] Kwalificatievragen worden gepresenteerd als begrijpelijke multiple-choice
- [ ] Simulatieresultaat wordt getoond met uitleg over het causale pad
- [ ] Hele flow is doorloopbaar zonder technische kennis
