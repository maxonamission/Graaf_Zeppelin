# Incident Response Plan — Graaf Zeppelin

> **Versie**: 1.0
> **Datum**: 15 maart 2026
> **Eigenaar**: Security Champion (zie sectie 6)
> **Herziening**: Jaarlijks of na elk P1/P2-incident

---

## 1. Doel

Dit document beschrijft hoe het team reageert op beveiligingsincidenten. Het doel is om de impact te beperken, herstel te versnellen en herhaling te voorkomen.

---

## 2. Incidentclassificatie

| Prioriteit | Omschrijving | Responstijd | Voorbeeld |
|-----------|-------------|-------------|-----------|
| **P1 — Kritiek** | Actief datalek, volledige systeem-compromis, of SECRET_KEY gelekt | **< 1 uur** | Database-dump op internet, alle gebruikerssessies ongeldig |
| **P2 — Hoog** | Gedeeltelijk datalek, account-overname van individuele gebruiker, of actieve exploit | **< 4 uur** | Credential stuffing met succesvolle logins, gestolen API-keys |
| **P3 — Gemiddeld** | Kwetsbaarheid ontdekt (niet actief misbruikt), verdachte activiteit in logs | **< 24 uur** | Kritieke CVE in dependency, onverklaarbare foutpieken in auditlogs |
| **P4 — Laag** | Informatieve melding, hardening-mogelijkheid, of minor misconfiguratie | **< 1 week** | Verouderde dependency zonder bekende exploit, ontbrekende header |

---

## 3. Escalatiepaden

### 3.1 Contactlijst

| Rol | Wie | Bereikbaar via | Wanneer |
|-----|-----|---------------|---------|
| **Security Champion** | [Naam invullen] | Telefoon + e-mail | Altijd bij P1/P2 |
| **Lead Developer** | [Naam invullen] | Telefoon + e-mail | Bij P1/P2, werkdagen bij P3 |
| **Product Owner** | [Naam invullen] | E-mail | Bij P1 (communicatie naar klanten) |
| **Hosting/infra** | [Naam/partij invullen] | Ticketsysteem | Bij P1/P2 (server-toegang nodig) |

### 3.2 Escalatieregel

1. Ontdekker meldt incident bij Security Champion
2. Security Champion classificeert (P1–P4) en informeert Lead Developer
3. Bij P1/P2: Product Owner wordt direct geïnformeerd
4. Bij P1: hosting/infra-partij wordt ingeschakeld als servertoegang nodig is

---

## 4. Stappenplannen per incidenttype

### 4.1 Datalekken (database-compromis, gelekte API-keys)

**Detectie**: Auditlogs tonen onverwachte data-exports, externe melding, of API-keys verschijnen op publieke platforms.

| Stap | Actie | Wie |
|------|-------|-----|
| 1 | **Isoleer**: Blokkeer toegang tot de database (firewall/credentials wijzigen) | Infra |
| 2 | **Revoke**: Alle refresh tokens invalideren (`DELETE FROM refresh_tokens`) | Developer |
| 3 | **Rotate SECRET_KEY**: Genereer nieuwe sleutel, herstart applicatie | Developer + Infra |
| 4 | **Re-encrypt**: Alle BYOK-keys zijn onleesbaar na sleutelwissel — informeer gebruikers om keys opnieuw in te voeren | Developer |
| 5 | **Forensisch**: Bepaal scope (welke tabellen, welke periode, hoeveel gebruikers). Gebruik `python -m app.core.guard_analyst summary` op auditlogs om aanvalspatronen te identificeren | Security Champion |
| 6 | **Notificeer**: Informeer getroffen gebruikers (zie sectie 5) | Product Owner |
| 7 | **Post-mortem**: Schrijf incident report binnen 5 werkdagen | Security Champion |

### 4.2 Account-overname (credential stuffing, sessiediefstal)

**Detectie**: Auditlogs tonen `login_success` vanaf ongebruikelijk IP, of gebruiker meldt ongeautoriseerde activiteit.

| Stap | Actie | Wie |
|------|-------|-----|
| 1 | **Blokkeer account**: `UPDATE users SET is_active = false WHERE id = ?` | Developer |
| 2 | **Revoke tokens**: Verwijder alle refresh tokens van het account | Developer |
| 3 | **Analyseer**: Controleer auditlogs op acties uitgevoerd door het gecompromitteerde account | Security Champion |
| 4 | **Reset wachtwoord**: Stuur reset-instructies naar gebruiker via geverifieerd kanaal | Developer |
| 5 | **Controleer schaal**: Zijn er meer accounts getroffen? Gebruik `python -m app.core.guard_analyst summary` om patronen te identificeren (zelfde IP, tijdsvenster) | Security Champion |
| 6 | **Informeer gebruiker**: Bevestig welke data mogelijk is ingezien | Product Owner |

### 4.3 Denial of Service (overbelasting)

**Detectie**: Monitoring toont hoge responstijden, 5xx-fouten, of onbereikbaarheid.

| Stap | Actie | Wie |
|------|-------|-----|
| 1 | **Identificeer bron**: Controleer access logs op IP-patronen | Developer + Infra |
| 2 | **Blokkeer**: IP-blokkade op reverse proxy-niveau (Caddy/nginx) | Infra |
| 3 | **Schaal**: Overweeg tijdelijk opschalen als de aanval gedistribueerd is | Infra |
| 4 | **Monitor**: Controleer dat de applicatie herstelt na blokkade | Developer |
| 5 | **Harden**: Overweeg strengere rate limits op getroffen endpoints | Developer |

### 4.4 Kwetsbaarheid in dependency (CVE-melding)

**Detectie**: Dependabot/pip-audit melding, externe CVE-publicatie, of security advisory.

| Stap | Actie | Wie |
|------|-------|-----|
| 1 | **Triage**: Is de kwetsbaarheid relevant voor ons gebruik van de library? | Security Champion |
| 2 | **Classificeer**: P2 als actief exploitbaar, P3 als theoretisch risico | Security Champion |
| 3 | **Patch**: Update dependency, draai tests | Developer |
| 4 | **Deploy**: Breng patch naar productie | Developer + Infra |
| 5 | **Documenteer**: Voeg CVE-nummer en actie toe aan security log | Security Champion |

**SLA voor patches** (zie ook `docs/dependency-management.md`):
- Kritieke CVE: patch binnen **48 uur**
- Hoge CVE: patch binnen **1 week**
- Gemiddelde/lage CVE: volgende reguliere update-cyclus

---

## 5. Communicatieprotocol

### 5.1 Wanneer informeren we gebruikers?

| Situatie | Informeren? | Kanaal | Termijn |
|----------|-------------|--------|---------|
| Bevestigd datalek met persoonsgegevens | **Ja, verplicht** (AVG art. 34) | E-mail + in-app banner | < 72 uur |
| Gelekte API-keys van BYOK-gebruikers | **Ja** | E-mail (individueel) | < 24 uur |
| Account-overname van individuele gebruiker | **Ja** (betrokken gebruiker) | E-mail (individueel) | < 24 uur |
| Kwetsbaarheid ontdekt maar niet misbruikt | **Nee** | — | — |
| DDoS met tijdelijke onbeschikbaarheid | **Optioneel** | In-app statusmelding | Tijdens incident |

### 5.2 AVG-meldplicht

Bij een datalek met persoonsgegevens:
1. **Autoriteit Persoonsgegevens** informeren binnen **72 uur** (art. 33 AVG)
2. Betrokkenen informeren als het lek "waarschijnlijk een hoog risico inhoudt" (art. 34 AVG)
3. Registreer het lek in het **datalekregister** (intern document)

### 5.3 Communicatiesjabloon

> **Onderwerp**: Beveiligingsmelding — Graaf Zeppelin
>
> Geachte [naam],
>
> Wij informeren u dat wij op [datum] een beveiligingsincident hebben geconstateerd dat mogelijk impact heeft op uw account/gegevens.
>
> **Wat is er gebeurd**: [korte beschrijving]
> **Welke gegevens zijn betrokken**: [opsomming]
> **Wat wij hebben gedaan**: [genomen maatregelen]
> **Wat u kunt doen**: [aanbevolen acties, bijv. wachtwoord wijzigen, API-key roteren]
>
> Voor vragen kunt u contact opnemen via [contactgegevens].

---

## 6. Bewaartermijnen

| Gegevenstype | Bewaartermijn | Reden |
|-------------|--------------|-------|
| **Auditlogs** (JSON) | **1 jaar** | Forensisch onderzoek, compliance |
| **Incident reports** | **3 jaar** | Trendanalyse, juridische bescherming |
| **Access logs** (webserver) | **90 dagen** | Operationele troubleshooting |
| **Database backups** | **30 dagen** (rolling) | Herstelmogelijkheid na datacompromis |

---

## 7. Jaarlijkse oefening (tabletop exercise)

### Doel
Test het incident response plan zonder daadwerkelijk een incident te veroorzaken.

### Format
- **Frequentie**: 1× per jaar (bij voorkeur Q1)
- **Duur**: 1,5–2 uur
- **Deelnemers**: Security Champion, Lead Developer, Product Owner
- **Vorm**: Scenario wordt gepresenteerd, team doorloopt het stappenplan

### Voorbeeldscenario's

1. **SECRET_KEY op GitHub**: Een developer heeft per ongeluk de `.env` file gecommit. De key staat 3 uur publiek zichtbaar.
2. **Credential stuffing**: Auditlogs tonen 200 `login_success` events vanaf 15 verschillende IP-adressen in 10 minuten, voor accounts die normaal inactief zijn.
3. **Kritieke CVE in httpx**: CVE meldt remote code execution in httpx < 0.26.0. Wij gebruiken httpx 0.25.0.

### Evaluatie na oefening
- Was het escalatiepad duidelijk?
- Hadden we alle benodigde toegang (database, server, logs)?
- Zijn de contactgegevens actueel?
- Aanpassingen aan dit plan documenteren.

---

## 8. Beschikbare tooling

| Tool | Commando | Doel |
|------|----------|------|
| **Guard Analyst** | `python -m app.core.guard_analyst summary <log>` | Samenvatting van geblokkeerde LLM Guard-pogingen per patroon en gebruiker |
| **Guard Analyst** | `python -m app.core.guard_analyst prompt <log>` | Genereer LLM-prompt om geblokkeerde invoer te analyseren op nieuwe patronen |
| **Guard Analyst** | `python -m app.core.guard_analyst apply <response.json>` | Pas LLM-analyse toe: voeg nieuwe patronen toe aan `data/llm_guard_patterns.json` |
| **Bandit** | `bandit -r app/` | Statische analyse op Python-code voor beveiligingsfouten |
| **pip-audit** | `pip-audit` | Controleer dependencies op bekende CVE's |

---

## 9. Herziening

Dit plan wordt herzien:
- Na elk P1- of P2-incident (verplicht)
- Na de jaarlijkse tabletop exercise
- Bij significante architectuurwijzigingen
- Minimaal 1× per jaar, ongeacht bovenstaande
