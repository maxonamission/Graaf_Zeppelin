# Open vragen — input nodig van product owner

Om de overige backlog-stories op te kunnen pakken heb ik op een aantal punten
jouw keuzes en context nodig. Hieronder per epic de vragen.

---

## EPIC-05: Begeleide beleidsverkenning

### S05-01 Begeleide interventie-flow
1. **Welke stappen zie je precies voor de begeleide flow?** De story beschrijft:
   vraag → sliders → kwalificatie → simulatie → resultaat. Maar moet de gebruiker
   ook tussentijds kunnen bijsturen (bijv. terug naar een eerdere stap)?
2. **Moet de AI de beleidsvraag interpreteren en automatisch sliders selecteren,
   of kiest de gebruiker zelf welke sliders relevant zijn?**
   (Dit raakt ook S06-02.)
3. **Moet deze flow een aparte pagina worden, of een wizard/stepper binnen de
   bestaande chat-interface?**

### S05-02 Slider-kwalificatie UX
4. **Hoe wil je de kwalificatievragen presenteren?** Als cards met radio-buttons,
   als een slider per vraag, of als een gespreksachtige flow (een vraag per keer)?
5. **Moeten gebruikers hun eerdere antwoorden kunnen wijzigen, of is het een
   one-way flow?**

### S05-03 Resultaatpagina
6. **Welke informatie is het belangrijkst voor een beleidsmedewerker?**
   Opties: impact-scores per factor, causale paden (visueel), concrete
   aanbevelingen (via LLM), of een combinatie?
7. **Wil je een vergelijkingsweergave (voor/na interventie)?**

---

## EPIC-07: Businessmodel & toegang

### S07-01 t/m S07-04 (alle stories)
8. **Is er al een prijsmodel bepaald?** De stories beschrijven 3 opties
   (gratis tier, credits, BYOK). Welke wil je als eerste implementeren?
9. **Hoeveel gratis vragen per sessie?** De story noemt 1-2, maar is dat per
   sessie, per dag, of per maand?
10. **Wat is de gewenste credits-structuur?** Vast maandbedrag + flexibel
    bijkopen, of puur pay-per-query?
11. **Moet de BYOK-optie (eigen API key) een apart licentie-tier worden,
    of een add-on binnen een bestaand tier?**

---

## EPIC-08: Slider-kwalificatievragen validatie

### S08-01 Inhoudelijke review
12. **Zijn er domeinexperts beschikbaar voor review?** Zo ja, in welk format
    wil je hen de vragen voorleggen (spreadsheet, in-app, document)?
13. **Voor welke sportdisciplines moeten de vragen kloppen?** Alleen schaatsen
    (KNSB-context), of breder (voetbal, hockey, etc.)?

### S08-03 Discipline-specifieke vragen
14. **Zijn er specifieke sportdisciplines waarvoor je afwijkende
    kwalificatievragen wilt?** Bijv. shorttrack vs. marathon vs.
    kunstrijden — verschilt het beleid significant?

### S08-05 Gebruikerstest
15. **Zijn er testgebruikers (sportbondmedewerkers) beschikbaar?**
    Zo ja, hoeveel en wanneer?

---

## EPIC-10: Productie & deployment

### S10-02 PostgreSQL migratie
16. **Waar wordt de app gehost?** Eigen server, cloud (AWS/Azure/GCP),
    of een PaaS (Railway, Render, Fly.io)? Dit bepaalt de PostgreSQL-setup.
17. **Is er al een productie-database, of beginnen we from scratch?**

### S10-03 Monitoring & logging
18. **Welke monitoring-tooling gebruik je al?** (Sentry, Datadog, Grafana,
    of niets?) Ik kan een keuze voorstellen als er nog niets is.

### S10-05 Meerdere modellen
19. **Zijn er al andere causale modellen in ontwikkeling?** Zo ja, in
    hetzelfde JSON-format als het sportdeelname-model?
20. **Moet de gebruiker kunnen wisselen tussen modellen, of is het per
    organisatie/licentie gekoppeld?**

---

## EPIC-09: Stabiliteit & kwaliteit

### S09-06 Onboarding
21. **Welke tone-of-voice wil je voor de onboarding?** Formeel
    (overheids-achtig) of informeel (startup-achtig)?
22. **Moet de onboarding overgeslagen kunnen worden door terugkerende
    gebruikers?**

---

## Prioritering

23. **Wat is de gewenste volgorde van de epics na de huidige ronde?**
    Suggestie: EPIC-05 (beleidsverkenning) eerst, dan EPIC-07 (business),
    dan EPIC-10 (productie). Klopt dat met jouw prioriteiten?
