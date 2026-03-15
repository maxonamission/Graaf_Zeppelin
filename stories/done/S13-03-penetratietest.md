# S13-03 — Penetratietest plannen en uitvoeren

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: HOOG
**Geschatte omvang**: L
**Status:** ✅ Done (handleiding opgeleverd — uitvoering bij productie-deployment)

## Doel

Een onafhankelijke penetratietest (pentest) laat een externe specialist de applicatie aanvallen alsof het een echte aanvaller is. Dit valideert of de maatregelen uit EPIC-11 in de praktijk standhouden.

## Waarom dit belangrijk is

De beveiligingsaudit (EPIC-11) is een *code review* — we hebben de broncode bekeken en bekende patronen gecontroleerd. Een pentest gaat verder: het test de *draaiende* applicatie, inclusief configuratie, netwerkverkeer, en combinaties van kwetsbaarheden die bij code review niet altijd opvallen.

Zoals de collega terecht opmerkt: "De kwaliteit van de implementatie, regelmatige updates en penetratietests zijn cruciaal." De code kan correct zijn, maar een fout in de server-configuratie kan de hele beveiliging ondermijnen.

## Acceptatiecriteria

- [ ] Scope vastgesteld (welke endpoints, welke rollen, welke omgeving)
- [ ] Pentest uitgevoerd door onafhankelijke partij (niet de ontwikkelaar)
- [ ] Testcategorieën minimaal:
  - Authenticatie en sessiebeheer
  - Autorisatiebypass (horizontaal en verticaal)
  - Input-injectie (SQL, XSS, prompt injection)
  - Business logic (credits manipulatie, licentie-omzeiling)
  - Configuratie (headers, TLS, cookie-flags)
- [ ] Rapport ontvangen met bevindingen, ernst en aanbevelingen
- [ ] Alle KRITIEKE en HOGE bevindingen opgelost
- [ ] Hertest uitgevoerd op opgeloste bevindingen

## Afhankelijkheden

- S13-01 (threat model) — bepaalt prioriteiten voor de testscope
- De applicatie moet in een testomgeving draaien die productie nabootst
