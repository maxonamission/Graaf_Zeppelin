# S05-02: Slider-kwalificatie UX

**Epic:** EPIC-05 Begeleide beleidsverkenning
**Status:** ✅ Done
**Prioriteit:** Midden

## User Story

**Als** beleidsmedewerker
**Wil ik** duidelijke feedback krijgen bij het beantwoorden van kwalificatievragen
**Zodat** ik beter begrijp wat mijn antwoorden betekenen voor de simulatie

## Acceptatiecriteria

- [x] Voortgangsbalk toont hoeveel vragen beantwoord zijn
- [x] Percentage-badge in header van stap 2
- [x] Mini-balkje per slider toont de resulterende waarde visueel (kleurgecodeerd)
- [x] Help-tekst wordt getoond bij kwalificatievragen (als aanwezig in model)
- [x] Slider-nummer indicator per kaart
- [x] updateQualifierProgress() wordt aangeroepen bij elke interactie

## Technische details

- `app/templates/wizard.html` — Enhanced qualifier cards met voortgang
- Visuele feedback via dynamische CSS class-switching (ok/warning/danger)
