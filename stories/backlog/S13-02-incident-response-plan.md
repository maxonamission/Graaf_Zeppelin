# S13-02 — Incident response plan

**Epic**: EPIC-13 Beveiligingsvervolg
**Prioriteit**: HOOG
**Geschatte omvang**: M
**Status:** 🔲 Backlog

## Doel

Een incident response plan beschrijft wat het team doet als er een beveiligingsincident plaatsvindt. Zonder dit plan gaat er kostbare tijd verloren aan afstemming terwijl een incident escaleert.

## Waarom dit belangrijk is

De auditlogging (S11-04) en geautomatiseerde scans (S11-05) zorgen ervoor dat we verdachte activiteiten *kunnen detecteren*. Maar detectie zonder actieplan is als een brandalarm zonder ontruimingsplan. Dit document beschrijft wie er belt, wie er handelt, en hoe we communiceren.

## Acceptatiecriteria

- [ ] Incidentclassificatie gedefinieerd (P1-P4 met voorbeelden per categorie)
- [ ] Contactlijst met escalatiepaden (wie wordt wanneer gebeld)
- [ ] Stappenplan per incidenttype:
  - Datalekken (database-compromis, gelekte API-keys)
  - Account-overname (credential stuffing, sessie-diefstal)
  - Denial of Service (overbelasting)
  - Kwetsbaarheid in dependency (CVE-melding)
- [ ] Communicatieprotocol: wanneer en hoe informeer je gebruikers
- [ ] Bewaartermijnen voor auditlogs en forensische gegevens
- [ ] Jaarlijkse oefening ingepland (tabletop exercise)
- [ ] Document opgeleverd als `docs/incident-response-plan.md`

## Afhankelijkheden

- S11-04 (auditlogging) — al afgerond
- S11-05 (geautomatiseerde scans) — al afgerond
