# S07-04: Eigen LLM-optie (BYOK met modellicentie)

**Epic:** EPIC-07 Businessmodel & toegang
**Status:** 🔲 Backlog
**Prioriteit:** Midden

## User Story

**Als** organisatie met een eigen LLM-abonnement
**Wil ik** mijn eigen API key koppelen en een vaste maandbijdrage betalen voor het model
**Zodat** ik onbeperkt vragen kan stellen tegen een voorspelbare prijs

## Beschrijving

Alternatief prijsmodel voor organisaties die al een LLM-provider gebruiken:

- Gebruiker koppelt eigen API key (OpenAI, Anthropic)
- Betaalt een vaste maandelijkse bijdrage voor toegang tot het causaal model
- Geen limiet op aantal vragen (LLM-kosten zijn voor eigen rekening)
- Geschikt voor power users en grotere organisaties

## Acceptatiecriteria

- [ ] BYOK-flow: gebruiker voert eigen API key in (al gebouwd, zie S03-02)
- [ ] Maandelijkse modellicentie: vast bedrag per maand
- [ ] Geen query-limiet bij BYOK (alleen modellicentie vereist)
- [ ] Key wordt veilig opgeslagen (encrypted, niet in logs)
- [ ] Duidelijke uitleg: "je LLM-kosten betaal je zelf aan je provider"
