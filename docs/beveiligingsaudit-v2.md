# Beveiligingsaudit — Graaf Zeppelin v2

> **Datum**: 15 maart 2026
> **Scope**: Volledige codebase (backend, frontend, infra, configuratie)
> **Beoordelingskaders**: OWASP Top 10 (2021), CWE/SANS Top 25, OWASP ASVS v4.0, OWASP Top 10 for LLM Applications
> **Doel**: Identificeer kwetsbaarheden en misbruikmogelijkheden vóór productie-deployment

---

## Managementsamenvatting

De applicatie heeft een solide functionele basis maar bevat **4 kritieke**, **7 hoge**, **8 gemiddelde** en **4 lage** beveiligingsrisico's die opgelost moeten worden vóór productie-inzet. De meest urgente problemen zitten in de authenticatielaag (wachtwoordhashing, tokenbeveiliging), de API-laag (rate limiting, input-validatie, autorisatiecontroles) en de frontend (XSS via innerHTML, ontbrekende CSP/SRI).

**Geen van de gevonden kwetsbaarheden is op dit moment actief exploiteerbaar** omdat de applicatie nog niet publiek draait. Alle bevindingen zijn preventief.

---

## Beoordelingsstandaarden

| Standaard | Versie | Toegepast op |
|-----------|--------|-------------|
| **OWASP Top 10** | 2021 | Alle bevindingen — primaire classificatie |
| **CWE (Common Weakness Enumeration)** | v4.14 | Technische classificatie per bevinding |
| **OWASP ASVS** | v4.0.3 | Verificatiecriteria voor authenticatie, sessies, cryptografie |
| **OWASP Top 10 for LLM Applications** | 2025 | LLM-specifieke risico's (prompt injection, output handling, leakage) |
| **NIST SP 800-63B** | Rev. 3 | Wachtwoordbeleid en authenticatie-eisen |

### Ernstclassificatie

| Ernst | Betekenis | Actie |
|-------|-----------|-------|
| **KRITIEK** | Direct exploiteerbaar, data-compromis mogelijk | Fixen vóór productie |
| **HOOG** | Significant risico bij gerichte aanval | Fixen vóór productie |
| **GEMIDDELD** | Risico bij combinatie met andere kwetsbaarheden | Fixen binnen 30 dagen na launch |
| **LAAG** | Best practice, beperkt risico | Plannen voor toekomstige sprint |

---

## Bevindingen

### KRITIEK

#### K1. Zwakke wachtwoordhashing (HMAC-SHA256)

| | |
|---|---|
| **Ernst** | KRITIEK |
| **OWASP** | A02:2021 Cryptographic Failures |
| **CWE** | CWE-916 (Insufficient Computational Effort) |
| **ASVS** | V2.4.1 — Gebruik bcrypt, scrypt, argon2 met voldoende cost factor |
| **Bestand** | `app/core/auth.py:20-24` |

**Probleem**: Wachtwoorden worden gehasht met HMAC-SHA256. Dit is een message authentication code, geen password hashing function. Het mist *computational cost* (key stretching) waardoor brute-force aanvallen met GPU's triviaal zijn (~10 miljard hashes/sec vs ~10.000/sec voor bcrypt).

**Huidig**:
```python
h = hmac.new(salt.encode(), password.encode(), hashlib.sha256).hexdigest()
```

**Moet worden**: bcrypt (cost factor 12+) of argon2id.

**Misbruikscenario**: Aanvaller die database-dump verkrijgt kan alle wachtwoorden kraken in minuten.

---

#### K2. Hardcoded geheime sleutel in broncode

| | |
|---|---|
| **Ernst** | KRITIEK |
| **OWASP** | A02:2021 Cryptographic Failures |
| **CWE** | CWE-798 (Hard-Coded Credentials) |
| **ASVS** | V6.4.1 — Cryptografische sleutels niet in broncode |
| **Bestand** | `app/config.py:7` |

**Probleem**: De JWT-ondertekeningssleutel heeft een hardcoded default waarde (`"dev-secret-key-change-in-production"`) die zichtbaar is in de Git-historie. Als deze niet overschreven wordt in productie, kan elke aanvaller geldige JWT-tokens smeden.

**Misbruikscenario**: Aanvaller creëert token met `{"sub": "admin@org.nl"}` → volledige account-overname.

---

#### K3. API-keys in request bodies (plaintext transmissie)

| | |
|---|---|
| **Ernst** | KRITIEK |
| **OWASP** | A02:2021 Cryptographic Failures |
| **CWE** | CWE-319 (Cleartext Transmission of Sensitive Information) |
| **ASVS** | V9.1.1 — TLS voor alle gevoelige data |
| **Bestanden** | `app/api/reasoning.py:22`, `app/api/wizard.py:48` |

**Probleem**: LLM API-keys worden als plaintext in request bodies verstuurd bij elke reasoning/wizard-aanroep. Zonder HTTPS-afdwinging zijn deze keys onderschepbaar. Bovendien kunnen keys in server-logs, proxy-logs of browser-netwerk-tabs terechtkomen.

**Moet worden**: Alleen opgeslagen keys (via `stored_key_id`) refereren, nooit raw keys per request.

---

#### K4. Geen rate limiting op authenticatie-endpoints

| | |
|---|---|
| **Ernst** | KRITIEK |
| **OWASP** | A07:2021 Identification and Authentication Failures |
| **CWE** | CWE-307 (Improper Restriction of Excessive Auth Attempts) |
| **ASVS** | V2.2.1 — Anti-automatisering op login, max 100 mislukte pogingen/uur |
| **Bestanden** | `app/api/auth.py:31-63, 66-90` |

**Probleem**: Login en registratie-endpoints hebben geen rate limiting. Een aanvaller kan onbeperkt wachtwoorden proberen (credential stuffing/brute force).

**Misbruikscenario**: Geautomatiseerde aanval probeert 10.000 wachtwoorden/minuut op een bekend e-mailadres.

---

### HOOG

#### H1. Geen wachtwoordbeleid

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A07:2021 Identification and Authentication Failures |
| **CWE** | CWE-521 (Weak Password Requirements) |
| **ASVS** | V2.1.1 — Minimaal 12 tekens, entropie-check |
| **Bestand** | `app/api/auth.py:19` |

**Probleem**: `password: str` accepteert elke string, inclusief `"a"`. Geen minimumlengte, geen complexiteitseisen conform NIST SP 800-63B.

---

#### H2. Ontbrekende secure cookie-flags

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A07:2021 Identification and Authentication Failures |
| **CWE** | CWE-614 (Sensitive Cookie Without 'Secure' Flag), CWE-1004 (Without 'HttpOnly') |
| **ASVS** | V3.4.1 — Cookies: Secure, HttpOnly, SameSite |
| **Bestanden** | `app/api/auth.py:62-63`, `app/api/deps.py:15` |

**Probleem**: Het access_token cookie wordt server-side gelezen maar de flags HttpOnly, Secure, en SameSite worden niet gezet. Hierdoor:
- JavaScript (en dus XSS-aanvallen) kan het token lezen
- Token wordt ook over HTTP verstuurd (niet alleen HTTPS)
- Geen CSRF-bescherming via SameSite

---

#### H3. Credits top-up zonder betaling of limiet

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A01:2021 Broken Access Control |
| **CWE** | CWE-269 (Improper Privilege Management) |
| **Bestand** | `app/api/license.py:200-237` |

**Probleem**: Het endpoint `/api/license/credits/topup` accepteert elk positief getal en trekt dit af van `queries_used`. Elke ingelogde gebruiker kan zichzelf onbeperkt credits geven:

```bash
POST /api/license/credits/topup {"amount": 999999}
# queries_used wordt max(0, X - 999999) = 0
```

**Moet worden**: Betaalintegratie of admin-goedkeuring vereist.

---

#### H4. Model-switching beïnvloedt alle gebruikers

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A01:2021 Broken Access Control |
| **CWE** | CWE-269 (Improper Privilege Management) |
| **Bestand** | `app/api/models.py:103-145` |

**Probleem**: `/api/models/switch` wijzigt `app.state.dag` — de globale grafiek voor álle gebruikers. Elke ingelogde gebruiker kan het actieve model wisselen. Geen rolcontrole.

**Misbruikscenario**: Kwaadwillende gebruiker wisselt naar een ander model → alle andere gebruikers krijgen verkeerde resultaten.

---

#### H5. Ontbrekende CSRF-bescherming

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A01:2021 Broken Access Control |
| **CWE** | CWE-352 (Cross-Site Request Forgery) |
| **ASVS** | V4.2.2 — CSRF-tokens op state-changing requests |
| **Bestanden** | Alle POST/DELETE endpoints |

**Probleem**: State-wijzigende endpoints (login, registratie, credits topup, model switch, conversatie verwijderen) hebben geen CSRF-bescherming. Omdat authenticatie via cookies gaat, worden deze automatisch meegestuurd door de browser.

---

#### H6. Geen input-lengtevalidatie op LLM-prompts

| | |
|---|---|
| **Ernst** | HOOG |
| **OWASP** | A03:2021 Injection |
| **CWE** | CWE-20 (Improper Input Validation) |
| **Bestanden** | `app/api/reasoning.py:21`, `app/api/wizard.py:32` |

**Probleem**: `query: str` en `question: str` hebben geen maximale lengte. Een aanvaller kan:
1. Extreem lange prompts sturen → LLM-kosten opdrijven
2. Prompt injection proberen
3. Server-resources uitputten

---

### GEMIDDELD

#### G1. Overdreven token-levensduur (24 uur)

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-613 (Insufficient Session Expiration) |
| **ASVS** | V3.3.1 — Tokens vervallen na inactiviteitsperiode |
| **Bestand** | `app/config.py:11` |

**Probleem**: Tokens zijn 24 uur geldig. Een gestolen token blijft een hele dag bruikbaar. Geen refresh-token mechanisme, geen invalidatie bij wachtwoordwijziging.

---

#### G2. JWT-algoritme niet gevalideerd bij decodering

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-347 (Improper Verification of Cryptographic Signature) |
| **Bestand** | `app/core/auth.py:65-92` |

**Probleem**: Bij het decoderen van JWT-tokens wordt niet gecontroleerd of het `alg` veld in de header `HS256` is. Een aanvaller zou een token met `"alg": "none"` kunnen proberen.

---

#### G3. Informatielekken via foutmeldingen

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-209 (Information Exposure Through Error Message) |
| **Bestanden** | `app/api/license.py:38`, `app/api/reasoning.py:197`, `app/api/auth.py:84` |

**Probleem**: `raise HTTPException(detail=str(e))` geeft interne exception-details door aan de client. Dit kan database-structuur, systeempaden of licentie-interne informatie lekken.

---

#### G4. Ontbrekende auditlogging

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-778 (Insufficient Logging) |
| **OWASP** | A09:2021 Security Logging and Monitoring Failures |
| **Bestanden** | Alle API-bestanden |

**Probleem**: Geen logging van beveiligingsrelevante events: mislukte logins, licentie-validatiefouten, API-key wijzigingen, model-switches, credit-mutaties.

---

#### G5. Sequentiële ID's (IDOR-risico)

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-639 (Authorization Bypass Through User-Controlled Key) |
| **Bestanden** | `app/models/conversation.py`, `app/api/conversations.py` |

**Probleem**: Conversaties gebruiken sequentiële integers als ID. Hoewel eigendomscontroles bestaan, zijn de ID's voorspelbaar. Een aanvaller kan alle ID's enumereren en via timing-analyse afleiden welke bestaan.

---

### LAAG

#### L1. Ontbrekende HTTP-beveiligingsheaders

| | |
|---|---|
| **Ernst** | LAAG |
| **CWE** | CWE-693 (Protection Mechanism Failure) |
| **Bestand** | `app/main.py` |

**Probleem**: Geen `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, `Strict-Transport-Security` headers. Caddy lost sommige hiervan op, maar de applicatie zelf stuurt ze niet mee.

---

#### L2. XSS-risico via innerHTML in templates

| | |
|---|---|
| **Ernst** | LAAG (gemitigeerd door escapeHtml) |
| **CWE** | CWE-79 (Cross-site Scripting) |
| **Bestanden** | `app/templates/dashboard.html`, `graph_viewer.html`, `license.html` |

**Probleem**: Meerdere templates gebruiken `innerHTML` met dynamische data. De `escapeHtml()` functie mitigeert dit grotendeels, maar niet alle paden gebruiken deze consistent. Server-side Jinja2 auto-escaping is wél actief.

---

#### L3. Account-enumeratie via registratiefoutmelding

| | |
|---|---|
| **Ernst** | LAAG |
| **CWE** | CWE-204 (Observable Response Discrepancy) |
| **Bestand** | `app/api/auth.py:50` |

**Probleem**: `"E-mailadres is al geregistreerd"` vertelt een aanvaller welke e-mailadressen een account hebben.

---

#### G6. Zwakke key-derivatie in KeyVault

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-327 (Use of Broken Cryptographic Algorithm) |
| **OWASP** | A02:2021 Cryptographic Failures |
| **Bestand** | `app/core/key_vault.py:21-23` |

**Probleem**: De Fernet-encryptiesleutel voor opgeslagen API-keys wordt afgeleid via een simpele `SHA-256(secret_key)`. Dit biedt geen key stretching. Als de `secret_key` zwak of gelekt is, zijn alle opgeslagen API-keys te ontsleutelen.

**Moet worden**: Proper KDF zoals PBKDF2 met ≥100.000 iteraties, of een apart beheerde encryptiesleutel (`ENCRYPTION_MASTER_KEY` env var).

---

#### G7. Geen SSL-afdwinging op PostgreSQL-verbinding (productie)

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-295 (Improper Certificate Validation) |
| **Bestand** | `app/db.py:8` |

**Probleem**: De database-verbinding dwingt geen SSL af in productie. Als de PostgreSQL-server op een ander netwerk draait, kunnen credentials en data onderschept worden.

**Moet worden**: `?sslmode=require` in de `DATABASE_URL` voor productie, of validatie bij opstart.

---

#### L4. Ontbrekende Subresource Integrity (SRI) op CDN-scripts

| | |
|---|---|
| **Ernst** | LAAG |
| **CWE** | CWE-829 (Inclusion of Functionality from Untrusted Control Sphere) |
| **OWASP** | A06:2021 Vulnerable and Outdated Components |
| **Bestanden** | `app/templates/base.html:8`, `app/templates/graph_viewer.html:5` |

**Probleem**: Externe scripts (htmx van unpkg, D3 van d3js.org) worden geladen zonder `integrity` attribuut. Als de CDN gecompromitteerd wordt, kan kwaadaardige code geïnjecteerd worden.

**Moet worden**:
```html
<script src="https://d3js.org/d3.v7.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

---

### AANVULLEND: Frontend-specifieke bevindingen (uit template-audit)

De volgende bevindingen kwamen uit de gedetailleerde template-analyse en zijn al verwerkt in de bestaande stories:

#### F1. DOM-XSS via innerHTML met API-data (→ S11-02)

| | |
|---|---|
| **Ernst** | HOOG |
| **CWE** | CWE-79 (Cross-site Scripting) |
| **Bestanden** | `login.html:46`, `register.html:65`, `graph_viewer.html:146,217` |

**Probleem**: Foutmeldingen van de API (`data.detail`) worden via `innerHTML` in de DOM geplaatst zonder escaping. In `login.html` en `register.html` wordt dit niet via `escapeHtml()` gedaan. In `graph_viewer.html` worden domein-namen en factor-ID's in `onclick` attributen geïnterpoleerd zonder volledige escaping.

**Voorbeeld**: `login.html:46`:
```javascript
document.getElementById('login-error').innerHTML =
    `<div class="alert alert-error">${data.detail}</div>`;
```

**Fix**: Gebruik `.textContent` voor data, of `escapeHtml()` consistent op alle paden.

---

#### F2. Cookie zonder HttpOnly/Secure via JavaScript (→ S11-01)

| | |
|---|---|
| **Ernst** | HOOG |
| **CWE** | CWE-614 |
| **Bestanden** | `login.html:43`, `register.html:62`, `base.html:24` |

**Probleem**: Het access_token wordt via JavaScript in een cookie gezet (`document.cookie = ...`) zonder `Secure` of `HttpOnly` flags. De token moet server-side via `Set-Cookie` header worden gezet.

---

#### F3. Ontbrekende Content Security Policy (→ S11-02)

| | |
|---|---|
| **Ernst** | HOOG |
| **CWE** | CWE-693 (Protection Mechanism Failure) |
| **Bestand** | `app/main.py` (middleware), `base.html` |

**Probleem**: Geen CSP-header. Alle inline scripts en styles zijn toegestaan. In combinatie met de innerHTML-kwetsbaarheden is dit een risico-vermenigvuldiger. Aanbevolen:
```
Content-Security-Policy: default-src 'self'; script-src 'self' https://unpkg.com https://d3js.org; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'
```

---

#### F4. Onvolledige escape-functie in reasoning.html (→ S11-02)

| | |
|---|---|
| **Ernst** | GEMIDDELD |
| **CWE** | CWE-79 |
| **Bestand** | `app/templates/reasoning.html:418-420` |

**Probleem**: `escapeAttr()` escaped alleen quotes, niet backslashes of HTML-entities. Wordt gebruikt voor `onclick` attributen. Beter: `JSON.stringify()` gebruiken voor attribuut-waarden.

---

#### F5. Logout alleen client-side (→ S11-01)

| | |
|---|---|
| **Ernst** | LAAG |
| **CWE** | CWE-613 |
| **Bestand** | `base.html:24` |

**Probleem**: Uitloggen verwijdert alleen de cookie client-side. Er is geen server-side sessie-invalidatie. Het token blijft tot 24 uur geldig. Wordt opgelost met refresh-token mechanisme (S11-01).

---

## Samenvattingsmatrix

| # | Bevinding | Ernst | OWASP | CWE | Story |
|---|-----------|-------|-------|-----|-------|
| K1 | Zwakke wachtwoordhashing | KRITIEK | A02 | 916 | S11-01 |
| K2 | Hardcoded secret key | KRITIEK | A02 | 798 | S11-01 |
| K3 | API-keys in plaintext | KRITIEK | A02 | 319 | S11-02 |
| K4 | Geen rate limiting auth | KRITIEK | A07 | 307 | S11-01 |
| H1 | Geen wachtwoordbeleid | HOOG | A07 | 521 | S11-01 |
| H2 | Ontbrekende cookie-flags (backend + frontend) | HOOG | A07 | 614 | S11-01 |
| H3 | Credits topup onbeveiligd | HOOG | A01 | 269 | S11-03 |
| H4 | Model switch globaal | HOOG | A01 | 269 | S11-03 |
| H5 | Geen CSRF | HOOG | A01 | 352 | S11-02 |
| H6 | Geen input-lengtevalidatie | HOOG | A03 | 20 | S11-02 |
| F1 | DOM-XSS via innerHTML (login, register, graph) | HOOG | A03 | 79 | S11-02 |
| G1 | Token 24 uur geldig | GEMIDDELD | A07 | 613 | S11-01 |
| G2 | JWT alg niet gevalideerd | GEMIDDELD | A02 | 347 | S11-01 |
| G3 | Foutmeldingen lekken info | GEMIDDELD | A09 | 209 | S11-04 |
| G4 | Geen auditlogging | GEMIDDELD | A09 | 778 | S11-04 |
| G5 | Sequentiële ID's | GEMIDDELD | A01 | 639 | S11-03 |
| F3 | Ontbrekende CSP-header | GEMIDDELD | A03 | 693 | S11-02 |
| G6 | Zwakke key-derivatie KeyVault | GEMIDDELD | A02 | 327 | S11-01 |
| G7 | Geen SSL op PostgreSQL (prod) | GEMIDDELD | A02 | 295 | S11-02 |
| L1 | Geen overige security headers | LAAG | A05 | 693 | S11-02 |
| L2 | Onvolledige escapeAttr() | LAAG | A03 | 79 | S11-02 |
| L3 | Account-enumeratie | LAAG | A07 | 204 | S11-01 |
| L4 | Geen SRI op CDN-scripts | LAAG | A06 | 829 | S11-02 |

---

## OWASP Top 10 for LLM Applications — Beoordeling

> **Datum**: 15 maart 2026
> **Aanleiding**: De applicatie integreert externe LLM-providers (OpenAI, Anthropic) via BYOK. Dit vereist specifieke beveiliging conform de OWASP Top 10 for LLM Applications.
> **Bestand**: `app/core/llm_guard.py` — centrale guard-module

### Overzicht

| # | Risico | Status | Toelichting |
|---|--------|--------|-------------|
| **LLM01** | Prompt Injection | ✅ Gemitigeerd | `check_prompt_injection()` blokkeert patronen (NL+EN) vóór de LLM-aanroep. Patronen configureerbaar via `data/llm_guard_patterns.json` (S11-06). Post-hoc analyse via `guard_analyst.py` ontdekt nieuwe patronen (S11-07). Audit logging van geblokkeerde pogingen. |
| **LLM02** | Sensitive Information Disclosure | ✅ OK | API-keys versleuteld (Fernet+PBKDF2, 480k iteraties). BYOK-model: keys nooit in requests of logs. Foutmeldingen gemaskeerd. |
| **LLM03** | Supply Chain | ✅ OK | `pip-audit` en `semgrep` in CI (GitHub Actions). Dependency CVE-scan per kwartaal. |
| **LLM04** | Data and Model Poisoning | ✅ Laag risico | Causaal model is server-side JSON, geen gebruikers-upload. Modelselectie vereist admin-rol. |
| **LLM05** | Improper Output Handling | ✅ Gemitigeerd | `sanitize_llm_output()` neutraliseert HTML/script-tags in LLM-responses vóór teruggave aan client. Voorkomt XSS bij browser-rendering. |
| **LLM06** | Excessive Agency | ✅ OK | LLM heeft geen tools, geen function calling, geen code execution. Uitsluitend tekstgeneratie. |
| **LLM07** | System Prompt Leakage | ✅ Gemitigeerd | `check_prompt_leakage_attempt()` detecteert extractiepogingen (NL+EN). Patronen configureerbaar via JSON (S11-06). Systeemprompt bevat expliciete "nooit onthullen"-regel. Audit logging. |
| **LLM08** | Vector and Embedding Weaknesses | N.v.t. | Geen RAG of embeddings. Factor-selectie via keyword matching (`find_relevant_factors()`). |
| **LLM09** | Misinformation | ✅ Gemitigeerd | `validate_response_factors()` controleert of genoemde factoren in het causale model voorkomen. Temperature=0.1. Systeemprompt dwingt causale constraints af. |
| **LLM10** | Unbounded Consumption | ✅ OK | Rate limiting (slowapi), quota per tier (2/dag gratis, 1000/maand professioneel), max_tokens=2000, httpx timeout=60s. |

### Testdekking

41 tests in `tests/test_llm_guard.py`:
- 17 tests: prompt injection detectie (bekende patronen)
- 6 tests: valse positieven (normale vragen niet geblokkeerd)
- 6 tests: output sanitisatie (XSS-vectoren, markdown-behoud)
- 8 tests: system prompt leakage detectie
- 4 tests: valse positieven bij leakage-detectie

---

## Herhalingsschema

Deze audit is bedoeld als **herhaalbaar proces**. Voer opnieuw uit bij:

| Trigger | Wat |
|---------|-----|
| **Elke major release** | Volledige audit (dit document) |
| **Nieuwe API-endpoints** | Minimaal: input-validatie, authz, rate limiting check |
| **Dependency-update** | `pip-audit` of `safety check` draaien |
| **Na security incident** | Gerichte audit op getroffen component |
| **Elk kwartaal** | Geautomatiseerde scan (bijv. `bandit`, `semgrep`) |

### Geautomatiseerde tooling (aanbevolen)

```bash
# Python security linter
pip install bandit
bandit -r app/ -f json -o reports/bandit.json

# Dependency vulnerability check
pip install pip-audit
pip-audit --format json --output reports/pip-audit.json

# SAST (Static Application Security Testing)
pip install semgrep
semgrep --config "p/python" --config "p/owasp-top-ten" app/
```
