# S06-05: Foutafhandeling LLM

**Epic:** EPIC-06 AI-assistent bruikbaar maken
**Status:** 🔲 Backlog
**Prioriteit:** Midden

## User Story

**Als** beleidsmedewerker
**Wil ik** duidelijke foutmeldingen zien als er iets misgaat met de AI
**Zodat** ik weet wat ik moet doen (key controleren, opnieuw proberen, etc.)

## Acceptatiecriteria

- [ ] API-fout: "De AI-dienst is tijdelijk niet bereikbaar. Probeer het later opnieuw."
- [ ] Ongeldige key: "Je API-sleutel is ongeldig. Controleer deze in je accountinstellingen."
- [ ] Rate limit: "Je hebt het maximum aantal vragen bereikt. Wacht X minuten."
- [ ] Quota bereikt: "Je maandelijkse limiet is bereikt. Upgrade je account of wacht tot volgende maand."
- [ ] Timeout: duidelijke indicatie dat het antwoord te lang duurt
