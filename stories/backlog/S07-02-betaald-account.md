# S07-02: Betaald account met keuze

**Epic:** EPIC-07 Businessmodel & toegang
**Status:** 🔲 Backlog
**Prioriteit:** Hoog

## User Story

**Als** beleidsmedewerker met een betaald account
**Wil ik** kunnen kiezen hoe ik de AI-assistent gebruik
**Zodat** ik de optie heb die het beste bij mijn organisatie past

## Beschrijving

Betaalde gebruikers krijgen meer mogelijkheden. Twee hoofdopties:

### Optie A: Wij leveren het LLM

- Gebruiker hoeft geen eigen API key te hebben
- Wij bieden toegang tot het LLM als onderdeel van het abonnement
- **Vast deel met credits**: maandelijks een vast aantal vragen inbegrepen
- **Flexibel deel**: extra vragen bovenop het vaste quotum (pay-as-you-go of bundels)

### Optie B: Eigen LLM (BYOK) met modellicentie

- Gebruiker koppelt eigen LLM (eigen API key)
- Betaalt een vaste maandelijkse bijdrage voor toegang tot het causaal model
- Geen limiet op aantal vragen (kosten zijn voor eigen rekening bij LLM-provider)
- Voordeliger voor power users met veel vragen

## Acceptatiecriteria

- [ ] Twee duidelijke opties op de accountpagina
- [ ] Optie A: credits-systeem met vast + flexibel deel (zie S07-03)
- [ ] Optie B: BYOK-flow met maandelijkse modellicentie (zie S07-04)
- [ ] Duidelijke vergelijking: wanneer is welke optie voordeliger?
- [ ] Naadloze switch tussen opties mogelijk
