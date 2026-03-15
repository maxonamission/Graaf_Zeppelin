# S05-03: Resultaatpagina

**Epic:** EPIC-05 Begeleide beleidsverkenning
**Status:** Done
**Prioriteit:** Hoog

## User Story

**Als** beleidsmedewerker
**Wil ik** de simulatieresultaten overzichtelijk gepresenteerd zien
**Zodat** ik snel kan zien welke verbanden versterkt of verzwakt worden

## Acceptatiecriteria

- [x] Samenvatting met 3 stat-kaarten: totaal, versterkt, verzwakt
- [x] Filter-tabs: Alles / Versterkt / Verzwakt
- [x] Impact-balkje per effect (breedte proportioneel aan magnitude)
- [x] Kleurcodering: groen = versterkt, rood = verzwakt
- [x] Verbeterde Markdown export met simulatieresultaten

## Technische details

- `app/templates/wizard.html` — Enhanced step 3 met stats, filters, impact bars
- filterEffects() voor client-side filtering
- renderEffectRows() met proportionele impact-balken
