# S13-01 — Threat model opstellen

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: HOOG
**Geschatte omvang**: M
**Status:** ✅ Done

## Doel

Een threat model beschrijft systematisch *wie* de applicatie kan aanvallen, *hoe* ze dat zouden doen, en *wat* de impact is. Zonder threat model zijn beveiligingsmaatregelen reactief ("we fixen wat we vinden") in plaats van proactief ("we beschermen wat het meest kwetsbaar is").

## Waarom dit belangrijk is

De beveiligingsaudit (EPIC-11) heeft alle bekende kwetsbaarheidspatronen afgevangen via OWASP Top 10 en CWE/SANS Top 25. Maar deze lijsten gaan over *generieke* kwetsbaarheden. Een threat model kijkt specifiek naar *deze* applicatie: welke data is het meest waardevol? Welke gebruikers hebben welke rechten? Waar zitten de grenzen met externe systemen (LLM-providers, database, CDN)?

## Acceptatiecriteria

- [ ] Alle actoren geïdentificeerd (anonieme bezoeker, gratis gebruiker, betalende gebruiker, analist, admin, LLM-provider, CDN)
- [ ] Per actor: welke acties kunnen ze uitvoeren, welke data kunnen ze benaderen
- [ ] Vertrouwensgrenzen (trust boundaries) in kaart gebracht: browser ↔ server, server ↔ database, server ↔ LLM API
- [ ] Top 5 bedreigingsscenario's uitgewerkt met waarschijnlijkheid en impact
- [ ] Restrisico's benoemd (risico's die we bewust accepteren, met onderbouwing)
- [ ] Document opgeleverd als `docs/threat-model.md`

## Aanpak

Gebruik het STRIDE-model (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) als structuur, toegepast op de architectuur van Graaf Zeppelin.

## Afhankelijkheden

- Geen (kan onafhankelijk worden opgepakt)
- Input van domeinexperts en/of security-specialist is wenselijk
