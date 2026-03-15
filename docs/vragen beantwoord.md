# Open vragen — input nodig van product owner

Om de overige backlog-stories op te kunnen pakken heb ik op een aantal punten
jouw keuzes en context nodig. Hieronder per epic de vragen.

---

## EPIC-05: Begeleide beleidsverkenning

### S05-01 Begeleide interventie-flow
1. **Welke stappen zie je precies voor de begeleide flow?** De story beschrijft:
   vraag → sliders → kwalificatie → simulatie → resultaat. Maar moet de gebruiker
   ook tussentijds kunnen bijsturen (bijv. terug naar een eerdere stap)?
	1. MK: Ja, een gebruiker moet zeker een stapje terug kunnen nemen. Omdat ze later in het proces misschien iets bedenken wat ze eerder al moeten doen. En dan nu willen aanpassen.
2. **Moet de AI de beleidsvraag interpreteren en automatisch sliders selecteren,
   of kiest de gebruiker zelf welke sliders relevant zijn?**
   (Dit raakt ook S06-02.)
	1. MK: Hier denk ik dat AIN een voorstel mag doen, maar wel een validatievraag bij de gebruiker. En dat de gebruiker ook altijd nog zelf kan aanpassen wat hij wil instellen.
3. **Moet deze flow een aparte pagina worden, of een wizard/stepper binnen de
   bestaande chat-interface?**
	1. MK: moeilijk te zeggen nog met zekerheid. Ik denk dat ik gebruikers eigenlijk altijd de mogelijkheid wil geven om over te stappen naar de begeleide flow?

### S05-02 Slider-kwalificatie UX
4. **Hoe wil je de kwalificatievragen presenteren?** Als cards met radio-buttons,
   als een slider per vraag, of als een gespreksachtige flow (een vraag per keer)?
	1. Deze vraag is niet volledig duidelijk. Ik denk dat ik - als een sliders meerdere  vragen heeft dan één kaart met de vragen en onderin de resulterende slider waarde. 
5. **Moeten gebruikers hun eerdere antwoorden kunnen wijzigen, of is het een
   one-way flow?**
	1. MK: wijzigen moet kunnen.

### S05-03 Resultaatpagina
6. **Welke informatie is het belangrijkst voor een beleidsmedewerker?**
   Opties: impact-scores per factor, causale paden (visueel), concrete
   aanbevelingen (via LLM), of een combinatie?
	1. MK: in de eerste plaats concrete aanbevelingen met als toelichting de veronderstelde causale paden. Visuele paden als optie maar tekst is al ok. Uitleg op taalniveau b2 zonder in technische termen als nodes en edges te vervallen. Zeg X beïnvloedt y Positief en Versterkt z, dat etc.
7. **Wil je een vergelijkingsweergave (voor/na interventie)?**
	1. MK: misschien, ik weet nog niet goed wat ik er van moet verwachten?

---

## EPIC-07: Businessmodel & toegang

### S07-01 t/m S07-04 (alle stories)
8. **Is er al een prijsmodel bepaald?** De stories beschrijven 3 opties
   (gratis tier, credits, BYOK). Welke wil je als eerste implementeren?
	1. MK: mede afhankelijk van complexiteit maar pilot met free en byok?
9. **Hoeveel gratis vragen per sessie?** De story noemt 1-2, maar is dat per
   sessie, per dag, of per maand?
	1. MK: zodra het gaat om gratis vragen, per dag? Of per gebruiker? Is het lastig om misbruik te voorkomen?
10. **Wat is de gewenste credits-structuur?** Vast maandbedrag + flexibel bijkopen, of puur pay-per-query?
	1. MK: Vast voor byok, betaling is dan bijdrage voor ontwikkeling model. Per query voor use my key :-)
11. **Moet de BYOK-optie (eigen API key) een apart licentie-tier worden, of een add-on binnen een bestaand tier?**
	1. MK: ik denk dus apart? 

---

## EPIC-08: Slider-kwalificatievragen validatie

### S08-01 Inhoudelijke review
12. **Zijn er domeinexperts beschikbaar voor review?** Zo ja, in welk format wil je hen de vragen voorleggen (spreadsheet, in-app, document)?
	1. MK: ja, document om te kunnen bespreken.
13. **Voor welke sportdisciplines moeten de vragen kloppen?** Alleen schaatsen (KNSB-context), of breder (voetbal, hockey, etc.)?
	1. MK: breder, model wordt doorontwikkeld om sportbreed over Sportdeelname te kunnen gaan. Invoeren sport vooraf leidt al tot eerste instelling van het model. Parameters worden aangeleverd samen met het model.

### S08-03 Discipline-specifieke vragen
14. **Zijn er specifieke sportdisciplines waarvoor je afwijkende  kwalificatievragen wilt?** Bijv. shorttrack vs. marathon vs. kunstrijden — verschilt het beleid significant?
	1. MK: nee, sportselector moet leiden tot vooraf bepaalde instellingen. Die worden aangeleverd. 

### S08-05 Gebruikerstest
15. **Zijn er testgebruikers (sportbondmedewerkers) beschikbaar?** Zo ja, hoeveel en wanneer?
	1. MK: ja, die verzorg ik.

---

## EPIC-10: Productie & deployment

### S10-02 PostgreSQL migratie
16. **Waar wordt de app gehost?** Eigen server, cloud (AWS/Azure/GCP), of een PaaS (Railway, Render, Fly.io)? Dit bepaalt de PostgreSQL-setup.
	1. MK: lastig te zeggen, heb daar nog geen idee van. In ieder geval in Europa. Paas of cloud, sowieso geen eigen server verwacht ik.
17. **Is er al een productie-database, of beginnen we from scratch?**
	1. MK: nee nog niets.

### S10-03 Monitoring & logging
18. **Welke monitoring-tooling gebruik je al?** (Sentry, Datadog, Grafana, of niets?) Ik kan een keuze voorstellen als er nog niets is.
	1. MK: geen tool nog, graag een voorstel.

### S10-05 Meerdere modellen
19. **Zijn er al andere causale modellen in ontwikkeling?** Zo ja, in hetzelfde JSON-format als het sportdeelname-model?
	1. MK: ja, zelfde uitgangspunten. 
20. **Moet de gebruiker kunnen wisselen tussen modellen, of is het per   organisatie/licentie gekoppeld?**
	1. MK: gebruiker kiest een sport en dat leidt tot instelling van het (generieke) model - of aanwijzen van het juiste model als meerdere sporten niet alleen met parameters alleen te modelleren zijn. 

---

## EPIC-09: Stabiliteit & kwaliteit

### S09-06 Onboarding
21. **Welke tone-of-voice wil je voor de onboarding?** Formeel (overheids-achtig) of informeel (startup-achtig)?
	1. MK: informeel maar wel professionneel. Het blijft b2b maar wel binnen een minder formele sector.
22. **Moet de onboarding overgeslagen kunnen worden door terugkerende gebruikers?**
	1. MK: ja, dat denk ik wel.

---

## Prioritering

23. **Wat is de gewenste volgorde van de epics na de huidige ronde?**  Suggestie: EPIC-05 (beleidsverkenning) eerst, dan EPIC-07 (business), dan EPIC-10 (productie). Klopt dat met jouw prioriteiten?
	1. MK: akkoord. 