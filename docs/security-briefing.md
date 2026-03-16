# Security Briefing — Herbruikbare standaarden en overwegingen

> **Bron**: Graaf Zeppelin-project (causaal redeneerplatform met LLM-integratie)
> **Doel**: Deze briefing vat alle beveiligingsbeslissingen, standaarden en patronen samen zodat ze als startpunt dienen voor elk nieuw webapplicatieproject — met of zonder AI-component.
> **Datum**: 16 maart 2026

---

## 1. Gehanteerde standaarden

| Standaard | Versie | Toepassing |
|-----------|--------|-----------|
| **OWASP Top 10** | 2021 | Classificatie van alle bevindingen en maatregelen |
| **OWASP ASVS** | 4.0.3 | Verificatie van authenticatie, sessies en cryptografie |
| **OWASP Top 10 for LLM Applications** | 2025 | LLM-specifieke risico's (prompt injection, output handling, system prompt leakage) |
| **NIST SP 800-63B** | — | Wachtwoordbeleid en authenticatie-eisen |
| **CWE/SANS Top 25** | — | Technische kwetsbaarheidsclassificatie |
| **STRIDE** | — | Methodologie voor threat modeling |
| **AVG / GDPR** | — | Meldplicht datalekken (art. 33/34) en bewaartermijnen |

**Aanbeveling voor nieuwe projecten**: Start met OWASP Top 10 als minimale baseline. Voeg ASVS toe voor applicaties met inlogfunctionaliteit. Voeg het LLM Top 10 toe zodra er een AI-component is.

---

## 2. Authenticatie & sessiebeheer

### 2.1 Wachtwoorden

| Aspect | Standaard | Implementatie |
|--------|-----------|--------------|
| Hashing | OWASP ASVS 2.4 | **bcrypt** (cost ≥ 12) of argon2id |
| Minimale lengte | NIST 800-63B | **12 tekens**, gemengd (hoofd/klein/cijfer/speciaal) |
| Rehashing | — | Automatisch bij login als het hash-algoritme is gewijzigd |
| Enumeration-preventie | OWASP A07 | Identieke foutmelding bij onbekend account en fout wachtwoord |

### 2.2 Tokens & sessies

| Aspect | Standaard | Implementatie |
|--------|-----------|--------------|
| Access token | JWT (HS256) | **30 minuten** levensduur |
| Refresh token | — | **7 dagen**, opaque, opgeslagen in database, single-use met rotatie |
| Cookie flags | OWASP ASVS 3.4 | `HttpOnly`, `Secure`, `SameSite=Lax` |
| SECRET_KEY | — | Minimaal 32 tekens, validatie bij opstart, crash bij ontbreken |

### 2.3 Rate limiting

| Endpoint | Limiet | Reden |
|----------|--------|-------|
| Login | 5/minuut per IP | Brute-force preventie |
| Registratie | 3/uur per IP | Account-spam preventie |
| API-breed | Naar behoefte | DoS-preventie |

**Tooling**: `slowapi` (Python/FastAPI) of vergelijkbare middleware.

---

## 3. Invoervalidatie & outputsanitisatie

### 3.1 Invoer

| Maatregel | Details |
|-----------|---------|
| Framework-validatie | **Pydantic** modellen op alle API-endpoints |
| Maximale lengte | 2.000 tekens voor vrije tekstvelden |
| SQL-injectie | Uitsluitend **ORM-queries** (SQLAlchemy), nooit raw SQL |
| Type-afdwinging | Strikte types; geen `Any` in request-modellen |

### 3.2 Uitvoer (browser)

| Maatregel | Details |
|-----------|---------|
| XSS-preventie | `textContent` in plaats van `innerHTML`; `escapeHtml()` helper |
| Content Security Policy | Specifieke `script-src` voor CDN's, met SRI-hashes |
| Security headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `HSTS` |
| SRI | Integrity-attributen op alle externe scripts (D3.js, htmx, etc.) |

### 3.3 CSRF

| Maatregel | Details |
|-----------|---------|
| Methode | Content-Type validatie op state-changing requests (POST/PUT/DELETE moeten `application/json` zijn) |
| Alternatief | Double-submit cookie of `fastapi-csrf-protect` als er formulieren zijn |

---

## 4. Autorisatie & toegangscontrole

### 4.1 RBAC-model

| Rol | Rechten |
|-----|---------|
| **user** | Eigen gesprekken, eigen API-keys, beperkte queries |
| **analyst** | Alles van user + uitgebreide analyses |
| **admin** | Alles + modelwissel, credits toekennen, gebruikersbeheer |

### 4.2 Ontwerpprincipes

| Principe | Implementatie |
|----------|--------------|
| Least privilege | `require_role()` dependency op elke route |
| Resource isolation | Gebruiker ziet alleen eigen data (WHERE user_id = current_user) |
| Onvoorspelbare ID's | **UUID's** in plaats van sequentiële integers voor resources |
| Gevoelige operaties | Expliciete admin-check; geen verborgen endpoints |

---

## 5. Cryptografie & sleutelbeheer

| Aspect | Standaard | Implementatie |
|--------|-----------|--------------|
| Key derivation | OWASP 2023 | **PBKDF2** met 480.000 iteraties |
| API-key encryptie | — | **Fernet** (AES-128-CBC + HMAC) met PBKDF2-afgeleide sleutel |
| Backward compatibility | — | **MultiFernet** voor migratie van oude naar nieuwe encryptie |
| Database SSL | S13-05 / G7 | `sslmode=require` of `verify-full` verplicht in productie |
| Sleutelrotatie | — | SECRET_KEY wijzigen invalideert alle tokens en BYOK-keys; gebruikers informeren |

**Aanbeveling**: Scheid de JWT-signeersleutel van de encryptiesleutel. Eén gecompromitteerde sleutel mag niet alles blootstellen.

---

## 6. LLM-specifieke beveiliging (OWASP LLM Top 10)

### 6.1 Prompt injection (LLM01)

| Laag | Maatregel |
|------|-----------|
| **Pre-flight** | Regex-detectie van 18+ patronen (NL + EN) vóór de LLM-aanroep |
| **Configuratie** | Patronen in extern JSON-bestand (`data/llm_guard_patterns.json`), aanpasbaar zonder deploy |
| **Fallback** | Hardcoded baseline als JSON ontbreekt |
| **Post-hoc** | Guard Analyst CLI analyseert geblokkeerde queries, stelt nieuwe patronen voor |

### 6.2 Outputsanitisatie (LLM05)

| Maatregel | Details |
|-----------|---------|
| Gevaarlijke tags | Regex-detectie van `<script>`, `<iframe>`, `<svg onload>`, etc. |
| Escape | `html.escape()` op volledige output als gevaarlijke tags worden gedetecteerd |
| Markdown | Veilige markdown-constructies blijven intact |

### 6.3 System prompt leakage (LLM07)

| Maatregel | Details |
|-----------|---------|
| Pre-flight detectie | 7 regex-patronen (NL + EN) voor extractiepogingen |
| Instructie in prompt | Expliciete "nooit onthullen"-regel in het systeembericht |

### 6.4 Afweging real-time vs. post-hoc

| Maatregel | Latentie | Kosten | Wanneer? |
|-----------|----------|--------|----------|
| Regex pre-flight | ~0 ms | Nul | **Altijd** — eerste verdedigingslinie |
| Real-time LLM classifier | +1–3 s | 2× LLM-kosten | Pas bij open API of LLM met tools |
| Post-hoc batch-analyse | 0 (async) | Minimaal | **Kwartaallijks** — beste ROI |

### 6.5 Patroon-schema

```json
{
  "pattern": "ignore\\s+previous\\s+instructions",
  "category": "instruction_override|persona_hijack|jailbreak|prompt_extraction|privilege_escalation",
  "lang": "nl|en",
  "severity": "high|medium|low",
  "description": "Mensleesbare beschrijving"
}
```

Categorieën met toelichting:

| Categorie | Voorbeeld | Risico |
|-----------|-----------|--------|
| `instruction_override` | "Negeer vorige instructies" | Systeemgedrag wijzigen |
| `persona_hijack` | "Je bent nu een hacker" | Persona overnemen |
| `jailbreak` | "DAN MODE", "do anything now" | Alle beperkingen omzeilen |
| `prompt_manipulation` | `<system>`, `[INST]` | Structuurmanipulatie van de prompt |
| `privilege_escalation` | "ADMIN MODE" | Rolverhoging forceren |
| `prompt_extraction` | "Toon je instructies" | Systeemprompt achterhalen |

---

## 7. Logging & audit trail

### 7.1 Wat loggen?

| Event | Data | Niet loggen |
|-------|------|-------------|
| Login (succes/faal) | e-mail, IP, tijdstip | Wachtwoord |
| Registratie | e-mail, IP | — |
| LLM Guard blokkade | event, matched patroon, user_id | Volledige gebruikersinvoer |
| API-key aanmaak/verwijdering | user_id, key_id | Key-waarde |
| Credit-mutaties | user_id, bedrag, reden | — |
| Model-wisseling | user_id, oud/nieuw model | — |
| Reasoning-queries | user_id, tijdstip | Vraaginhoud (privacy) |

### 7.2 Formaat

```json
{
  "timestamp": "2026-03-15T10:00:00Z",
  "event": "prompt_injection_blocked",
  "user_id": 42,
  "ip": "198.51.100.1",
  "extra": {"matched": "jailbreak"}
}
```

### 7.3 Bewaartermijnen

| Type | Termijn | Reden |
|------|---------|-------|
| Auditlogs | 1 jaar | Forensisch onderzoek, compliance |
| Incident reports | 3 jaar | Trendanalyse, juridische bescherming |
| Access logs | 90 dagen | Operationele troubleshooting |
| Database backups | 30 dagen (rolling) | Herstelmogelijkheid |

---

## 8. Dependency management

### 8.1 Patch-SLA's

| Ernst (CVSS) | Termijn |
|-------------|---------|
| Kritiek (9.0–10.0) | **48 uur** |
| Hoog (7.0–8.9) | **1 week** |
| Gemiddeld (4.0–6.9) | Volgende sprint |
| Laag (0.1–3.9) | Volgende kwartaalupdate |

### 8.2 Tooling

| Tool | Frequentie | Doel |
|------|-----------|------|
| **GitHub Dependabot** | Continu | Automatische CVE-meldingen |
| **pip-audit** | Kwartaallijks + bij elke CI-build | Bekende kwetsbaarheden in dependencies |
| **bandit** | Bij elke CI-build | Statische analyse op Python-code |
| **semgrep** | Bij elke CI-build | Patronen voor veelvoorkomende fouten |

### 8.3 Lock-strategie

Duaal model: `requirements.txt` (directe dependencies met versieranges) + `requirements-lock.txt` (exacte versies voor reproduceerbare builds).

---

## 9. Incident response — kernpunten

### 9.1 Classificatie

| Prioriteit | Responstijd | Voorbeeld |
|-----------|-------------|-----------|
| **P1 — Kritiek** | < 1 uur | Actief datalek, SECRET_KEY gelekt |
| **P2 — Hoog** | < 4 uur | Account-overname, gestolen API-keys |
| **P3 — Gemiddeld** | < 24 uur | Kwetsbaarheid ontdekt, verdachte logs |
| **P4 — Laag** | < 1 week | Verouderde dependency, ontbrekende header |

### 9.2 Kernstappen bij elk incident

1. **Isoleer** — beperk de schade (credentials roteren, accounts blokkeren)
2. **Analyseer** — bepaal scope met auditlogs en Guard Analyst
3. **Herstel** — patch, deploy, tokens invalideren
4. **Communiceer** — getroffen gebruikers informeren (AVG: < 72 uur bij persoonsgegevens)
5. **Documenteer** — post-mortem binnen 5 werkdagen

### 9.3 AVG-meldplicht

- Autoriteit Persoonsgegevens: binnen **72 uur** (art. 33)
- Betrokkenen informeren bij "hoog risico" (art. 34)
- Registreren in intern datalekregister

---

## 10. Threat modeling — STRIDE-checklist

Doorloop deze vragen voor elk nieuw project of elke significante feature:

### Spoofing (identiteitsvervalsing)
- [ ] Kunnen ongeauthenticeerde gebruikers bij beschermde endpoints?
- [ ] Zijn tokens voldoende beschermd (HttpOnly, Secure, korte TTL)?
- [ ] Is er accountenumeratie mogelijk via registratie/login/reset?

### Tampering (gegevensmanipulatie)
- [ ] Wordt alle invoer gevalideerd (type, lengte, formaat)?
- [ ] Kan een gebruiker andermans data wijzigen (IDOR)?
- [ ] Bij LLM: kan de gebruiker de systeemprompt manipuleren?

### Repudiation (ontkenning)
- [ ] Worden beveiligingsrelevante acties gelogd (wie, wat, wanneer)?
- [ ] Zijn logs onwijzigbaar door de gebruiker?

### Information Disclosure (informatielekken)
- [ ] Lekken foutmeldingen technische details (stack traces, queries)?
- [ ] Zijn API-keys en wachtwoorden versleuteld in de database?
- [ ] Bij LLM: welke data gaat naar de externe LLM-provider?

### Denial of Service
- [ ] Zijn er rate limits op authenticatie-endpoints?
- [ ] Zijn er limieten op resource-intensieve operaties (LLM-calls, uploads)?
- [ ] Kan één gebruiker het systeem voor anderen onbruikbaar maken?

### Elevation of Privilege (rechtenverheffing)
- [ ] Is er RBAC met least privilege?
- [ ] Zijn admin-functies expliciet afgeschermd?
- [ ] Kan een gebruiker zijn eigen rol wijzigen?

---

## 11. Security review-cadans

| Frequentie | Activiteit | Verantwoordelijke |
|-----------|-----------|-------------------|
| **Continu** | Dependabot-meldingen triagen | Developer |
| **Per CI-build** | bandit + semgrep + pip-audit | Automatisch |
| **Kwartaallijks** | LLM Guard audit log analyse | Security Champion |
| **Kwartaallijks** | Dependency-update cyclus | Developer |
| **Halfjaarlijks** | Handmatige security review | Security Champion |
| **Jaarlijks** | Penetratietest | Extern of Security Champion |
| **Jaarlijks** | Tabletop exercise (incident response) | Team |
| **Jaarlijks** | Threat model herzien | Security Champion |

---

## 12. Checklist voor nieuwe projecten

### Dag 1 — fundament

- [ ] SECRET_KEY-validatie bij opstart (crash bij ontbreken)
- [ ] Wachtwoordhashing met bcrypt/argon2id
- [ ] Pydantic-modellen op alle API-endpoints
- [ ] ORM-only database-queries
- [ ] Security headers middleware
- [ ] `.env` in `.gitignore`

### Week 1 — authenticatie & autorisatie

- [ ] JWT access + refresh tokens met korte TTL
- [ ] Rate limiting op login en registratie
- [ ] RBAC met `require_role()` dependency
- [ ] Cookie flags: HttpOnly, Secure, SameSite
- [ ] Identieke foutmeldingen voor login-fouten

### Sprint 2 — hardening

- [ ] Audit logging (JSON-formaat)
- [ ] CSP + SRI op externe scripts
- [ ] CSRF-bescherming
- [ ] Input-lengtebeperkingen
- [ ] Foutmeldingen zonder technische details

### Doorlopend

- [ ] bandit + pip-audit in CI
- [ ] Dependabot ingeschakeld
- [ ] Patch-SLA's gedefinieerd
- [ ] Incident response plan geschreven

### Bij LLM-integratie

- [ ] Prompt injection detectie (pre-flight regex)
- [ ] Output sanitisatie (HTML-escape)
- [ ] System prompt leakage detectie
- [ ] Patronen in extern JSON-bestand
- [ ] Post-hoc analyse workflow ingericht
- [ ] Data Processing Agreement met LLM-provider

---

## Bronnen

Alle maatregelen in deze briefing zijn geïmplementeerd en gedocumenteerd in het Graaf Zeppelin-project:

| Document | Inhoud |
|----------|--------|
| `docs/beveiligingsaudit-v2.md` | Volledige audit met 23 bevindingen en mitigaties |
| `docs/threat-model.md` | STRIDE-analyse met 10 actoren en 30+ dreigingen |
| `docs/incident-response-plan.md` | Classificatie, stappenplannen, communicatieprotocol |
| `docs/security-review-proces.md` | Jaarplanning, checklists, rolverdeling |
| `docs/dependency-management.md` | Patch-SLA's, tooling, updateschema |
| `stories/done/S11-01` t/m `S11-07` | Implementatiestories beveiliging |
| `stories/done/S13-01` t/m `S13-06` | Opvolging beveiligingsaudit |
