# Threat Model — Graaf Zeppelin

> **Datum**: 15 maart 2026
> **Methode**: STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
> **Scope**: Volledige applicatie inclusief externe integraties
> **Leeswijzer**: Dit document is geschreven voor zowel technische als niet-technische stakeholders. Technische details staan in ingesprongen blokken.

---

## 1. Systeemoverzicht

### Wat doet Graaf Zeppelin?

Graaf Zeppelin is een webapplicatie waarmee beleidsmedewerkers causale modellen verkennen en beleidsinterventies simuleren. De applicatie combineert een wetenschappelijk model (DAG) met kunstmatige intelligentie (LLM) om onderbouwde beleidsadviezen te genereren.

### Architectuurdiagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (gebruiker)                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Dashboard │  │ Redeneer- │  │ Beleids- │  │ Grafiek-      │  │
│  │           │  │ assistent │  │ verkenner│  │ viewer        │  │
│  └──────────┘  └───────────┘  └──────────┘  └───────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS (cookies + JSON)
                           │
        ═══════════════════╪═══════════════════  Vertrouwensgrens 1
                           │                     Browser ↔ Server
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI-SERVER                                │
│                                                                 │
│  ┌─────────┐  ┌───────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Auth    │  │ Reasoning │  │ Wizard   │  │ Graph/Models  │  │
│  │ (JWT)   │  │ API       │  │ API      │  │ API           │  │
│  └────┬────┘  └─────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       │             │              │                │           │
│  ┌────┴────┐  ┌─────┴─────┐  ┌────┴─────┐  ┌──────┴────────┐  │
│  │ Rate    │  │ LLM       │  │ Prompt   │  │ DAG Engine    │  │
│  │ Limiter │  │ Connector │  │ Builder  │  │ + Sliders     │  │
│  └─────────┘  └─────┬─────┘  └──────────┘  └───────────────┘  │
│                      │                                          │
│  ┌─────────────┐  ┌──┴──────────┐  ┌────────────────────────┐  │
│  │ Audit Log   │  │ Key Vault   │  │ License Manager        │  │
│  │ (JSON file) │  │ (Fernet)    │  │ (quota, tiers)         │  │
│  └─────────────┘  └─────────────┘  └────────────────────────┘  │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
  ═════════╪══════════════════════════════════╪═══  Vertrouwensgrens 2
           │ SQL (async)                      │     Server ↔ Database
           ▼                                  │
┌──────────────────────┐                      │
│  POSTGRESQL DATABASE │                      │
│                      │                      │
│  users               │         ═════════════╪═══  Vertrouwensgrens 3
│  licenses            │                      │     Server ↔ LLM-providers
│  refresh_tokens      │                      ▼
│  conversations       │         ┌────────────────────────┐
│  messages            │         │  EXTERNE LLM-PROVIDERS │
│  explorations        │         │                        │
│  user_api_keys (enc) │         │  ● OpenAI API          │
│  daily_usage         │         │  ● Anthropic API       │
└──────────────────────┘         └────────────────────────┘
```

---

## 2. Actoren

| Actor | Beschrijving | Toegangsniveau | Motivatie |
|-------|-------------|---------------|-----------|
| **Anonieme bezoeker** | Iemand die de website bezoekt zonder account | Alleen publieke pagina's (home, login, registratie) | Verkenning, eventueel kwaadaardig (scannen op kwetsbaarheden) |
| **Gratis gebruiker** | Geregistreerd met gratis licentie | Alle read-endpoints, 2 AI-vragen per dag | Normaal gebruik, mogelijk gratis-limiet omzeilen |
| **Betalende gebruiker** | Geregistreerd met standaard/premium licentie | Alle read-endpoints, quotum volgens tier | Normaal gebruik |
| **BYOK-gebruiker** | Betalende gebruiker met eigen API-sleutels | Idem + opgeslagen API-keys | Normaal gebruik, risico op key-lekken |
| **Analist** | Rol "analyst" (tussenrol) | Mogelijk uitgebreide read-rechten (momenteel gelijk aan user) | Data-analyse |
| **Admin** | Rol "admin" | Model wisselen, credits bijboeken | Beheer, per ongeluk of bewust misbruik |
| **Gecompromitteerd account** | Account waarvan de credentials zijn gelekt | Rechten van het gecompromitteerde account | Datadiefstal, misbruik LLM-tegoed |
| **Kwaadwillende insider** | Iemand met toegang tot de server of database | Volledige toegang | Datadiefstal, sabotage |
| **LLM-provider** | OpenAI of Anthropic als externe dienst | Ontvangt prompts en gebruikerscontext | Dataverzameling (conform hun privacybeleid) |
| **CDN-provider** | unpkg.com, d3js.org, cdn.jsdelivr.net | Levert JavaScript-bestanden aan de browser | Kan bij compromis kwaadaardige scripts injecteren |
| **Netwerkaanvaller** | Man-in-the-middle op het netwerk | Kan verkeer onderscheppen als geen TLS | Sessiediefstal, data-onderschepping |

---

## 3. Vertrouwensgrenzen

### Grens 1: Browser ↔ Server

**Wat er overheen gaat:**
- JWT access tokens (in HttpOnly cookies)
- Refresh tokens (in HttpOnly cookies, pad-beperkt)
- Gebruikersinvoer (vragen, sliderwaarden, registratiegegevens)
- API-responses (modeldata, AI-antwoorden, gesprekken)

**Bestaande bescherming:**
- HTTPS (via Caddy/reverse proxy in productie)
- CSRF-middleware (Content-Type check op state-wijzigende requests)
- SameSite=Lax cookies
- Security headers (CSP, X-Frame-Options, HSTS)
- Input-validatie (Pydantic, lengtelimieten)
- Rate limiting op auth-endpoints

**Risico's:**
- Prompt injection via gebruikersinvoer → LLM geeft misleidende antwoorden (gemitigeerd door `llm_guard.py` patroondetectie)
- Systeemprompt leakage → aanvaller achterhaalt interne instructies (gemitigeerd door leakage-detectie en expliciete "nooit onthullen"-regel)
- XSS als CSP omzeild wordt (inline scripts zijn toegestaan met `unsafe-inline`; LLM-output wordt gesaniteerd via `sanitize_llm_output()`)

### Grens 2: Server ↔ Database

**Wat er overheen gaat:**
- SQL-queries met gebruikersgegevens
- Wachtwoordhashes (bcrypt)
- Versleutelde API-keys (Fernet-tokens)
- Refresh token hashes (SHA-256)
- Licentiegegevens en gebruiksstatistieken

**Bestaande bescherming:**
- SQLAlchemy ORM (voorkomt SQL-injectie)
- Wachtwoorden als bcrypt-hashes (niet omkeerbaar)
- API-keys versleuteld met Fernet

**Risico's:**
- Geen SSL-afdwinging op de databaseverbinding (G7 uit audit)
- Bij databasecompromis: refresh token hashes zijn SHA-256 (niet bcrypt) — met de hash kan een aanvaller geen token reconstrueren, maar kan wel tokens invalideren

### Grens 3: Server ↔ LLM-providers

**Wat er overheen gaat:**
- Gebruikers-API-keys (ontsleuteld uit KeyVault, in TLS naar provider)
- Systeemprompts met DAG-context (factoren, relaties, domeinnamen)
- Gebruikersvragen in volledige tekst
- AI-antwoorden

**Bestaande bescherming:**
- TLS naar provider-API's (standaard bij httpx)
- API-keys nooit gelogd of in responses opgenomen
- Keys worden alleen in geheugen ontsleuteld, niet opgeslagen

**Risico's:**
- De LLM-provider ziet alle gebruikersvragen en de volledige modelcontext
- Bij een lek aan de kant van de provider zijn gebruikersvragen zichtbaar
- Prompt injection: een gebruiker kan proberen de systeemprompt te omzeilen (gemitigeerd door `llm_guard.py`; zie LLM01/LLM07)

---

## 4. Gevoelige gegevens (kroonjuwelen)

| Gegeven | Opslaglocatie | Versleuteling | Impact bij lekken |
|---------|--------------|--------------|-------------------|
| **Gebruikerswachtwoorden** | Database (`users.hashed_password`) | bcrypt (cost 12) | Laag — hashes zijn niet omkeerbaar bij sterke wachtwoorden |
| **LLM API-keys van gebruikers** | Database (`user_api_keys.encrypted_key`) | Fernet (AES-128-CBC) | **Hoog** — aanvaller kan LLM-kosten op rekening van gebruiker genereren |
| **Refresh tokens** | Database (`refresh_tokens.token_hash`) | SHA-256 (niet omkeerbaar) | Gemiddeld — hash alleen, maar bij database-compromis kan aanvaller tokens revoking |
| **JWT secret key** | Omgevingsvariabele (`SECRET_KEY`) | N.v.t. (nooit opgeslagen in DB) | **Kritiek** — kan geldige tokens voor elke gebruiker genereren |
| **Fernet-encryptiesleutel** | Afgeleid van `SECRET_KEY` via SHA-256 | N.v.t. | **Kritiek** — kan alle opgeslagen API-keys ontsleutelen |
| **Gesprekgeschiedenis** | Database (`messages.content`) | Geen versleuteling | Gemiddeld — bevat beleidsvragen, mogelijk gevoelige beleidsoverwegingen |
| **E-mailadressen** | Database (`users.email`) | Geen versleuteling | Gemiddeld — persoonsgegevens onder AVG |
| **Licentie-sleutels** | Database (`licenses.key`) | Geen versleuteling | Laag — sleutels zijn voor registratie, niet voor betaling |
| **Auditlogs** | Bestandssysteem (JSON) | Geen versleuteling | Laag — bevatten geen wachtwoorden of keys, wel e-mailadressen en IP's |

### Kritieke observatie

De `SECRET_KEY` is de enige sleutel waarvan de hele beveiliging afhangt:
- JWT-ondertekening → sessiediefstal van alle gebruikers
- Fernet key-derivatie → ontsleuteling van alle opgeslagen API-keys

Dit is een **single point of failure**. Als de SECRET_KEY lekt, zijn beide beveiligingslagen doorbroken.

---

## 5. STRIDE-analyse per vertrouwensgrens

### 5.1 Spoofing (identiteitsvervalsing)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| SP-1 | Aanvaller logt in met gestolen wachtwoord | 1 | bcrypt hashing, wachtwoordcomplexiteit (12 tekens, mixed), rate limiting (5/min) | **Laag** — brute force onpraktisch, maar credential stuffing met elders gelekte wachtwoorden blijft mogelijk |
| SP-2 | Aanvaller smeedt een JWT-token | 1 | SECRET_KEY validatie bij opstart (min 32 tekens, geen defaults), HS256 algoritme-check | **Laag** — alleen mogelijk bij lekken van SECRET_KEY |
| SP-3 | Aanvaller hergebruikt gestolen refresh token | 1 | Token rotatie, reuse-detectie (alle tokens van gebruiker worden ingetrokken), SHA-256 hashing, 7 dagen expiry | **Laag** — reuse-detectie maakt dit self-healing |
| SP-4 | Aanvaller registreert met vervalste organisatie | 1 | Licentie-key vereist bij registratie | **Gemiddeld** — licentie-key is het enige validatiemiddel; geen e-mailverificatie |

### 5.2 Tampering (gegevensvervalsing)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| TA-1 | Aanvaller wijzigt request-body om credits te manipuleren | 1 | Credits topup vereist ADMIN-rol, limiet 1-100 per keer | **Laag** |
| TA-2 | Aanvaller wijzigt model-switch request | 1 | Model switch vereist ADMIN-rol, pad-traversal preventie | **Laag** |
| TA-3 | Prompt injection via gebruikersvraag | 1→3 | Systeemprompt bevat constraints, antwoord-validatie, max 2000 tekens, **LLM Guard** (`llm_guard.py`) blokkeert 18 bekende injectiepatronen (NL+EN) vóór de LLM, audit logging van geblokkeerde pogingen | **Laag–Gemiddeld** — bekende patronen worden geblokkeerd; creatieve varianten blijven een risico |
| TA-4 | SQL-injectie via invoervelden | 1→2 | SQLAlchemy ORM (geparametriseerde queries), Pydantic validatie | **Laag** — ORM voorkomt directe SQL-injectie |
| TA-5 | Aanvaller wijzigt het causale model (JSON) | Server | Modelbestanden worden geladen van het bestandssysteem; geen upload-endpoint | **Laag** — vereist servertoegang |

### 5.3 Repudiation (ontkenning)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| RE-1 | Gebruiker ontkent een actie (login, query, model switch) | Alle | Gestructureerde auditlogging met timestamp, user_id, IP, event-type | **Laag** — alle beveiligingsrelevante acties worden gelogd |
| RE-2 | Admin ontkent credits te hebben bijgeboekt | 1 | Audit event `model_switched` en `credits_topup` (impliciet via license manager) | **Gemiddeld** — credits topup heeft momenteel geen apart audit event; afgeleid uit license manager logs |
| RE-3 | Auditlogs worden gemanipuleerd | Server | Logs staan op het bestandssysteem, geen tamper-detectie | **Gemiddeld** — bij servertoegang zijn logs bewerkbaar |

### 5.4 Information Disclosure (informatielekken)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| ID-1 | Aanvaller leest gesprekken van andere gebruikers | 1→2 | Eigendomscontrole op conversation endpoints, UUID-identificatie | **Laag** |
| ID-2 | Foutmeldingen onthullen systeeminformatie | 1 | Generieke foutmeldingen voor auth, LLM-fouten gelogd maar niet naar client | **Laag** |
| ID-3 | Account-enumeratie via registratie | 1 | Generiek foutbericht ("Registratie niet mogelijk") | **Laag** |
| ID-4 | LLM-provider ziet gebruikersvragen | 3 | Geen — dit is inherent aan het gebruik van externe LLM-diensten | **Gemiddeld** — gevoelige beleidsvragen worden naar externe diensten gestuurd |
| ID-5 | Database-dump onthult API-keys | 2 | Fernet-versleuteling, maar sleutel afgeleid van SECRET_KEY | **Gemiddeld** — bij lekken SECRET_KEY + database zijn keys te ontsleutelen |
| ID-6 | API-key zichtbaar in servergeheugen | Server | Key wordt ontsleuteld in geheugen voor de duur van de LLM-aanroep | **Laag** — kortstondig, vereist geheugentoegang tot de server |
| ID-7 | Databaseverkeer onderschept | 2 | Geen SSL-afdwinging op databaseverbinding | **Gemiddeld** — relevant als database op apart netwerksegment draait |

### 5.5 Denial of Service (onbeschikbaarheid)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| DS-1 | Brute force op login-endpoint | 1 | Rate limiting: 5/min per IP | **Laag** |
| DS-2 | Massale registraties | 1 | Rate limiting: 3/uur per IP, licentie-key vereist | **Laag** |
| DS-3 | Dure LLM-queries om kosten op te drijven | 1→3 | Query-lengte max 2000 tekens, credits/quotum-systeem, free-tier limiet | **Gemiddeld** — een betalende gebruiker kan binnen zijn quotum veel queries sturen |
| DS-4 | Uitputting van graph-endpoints (geen rate limiting) | 1 | Geen rate limiting op graph/reasoning/wizard endpoints | **Gemiddeld** — 36 van 39 endpoints hebben geen rate limiting |
| DS-5 | Grote hoeveelheid gelijktijdige simulaties | 1 | Geen expliciete concurrency-limiet | **Gemiddeld** — simulaties zijn CPU-intensief |
| DS-6 | LLM-provider onbeschikbaar | 3 | Foutafhandeling met nette foutmelding naar gebruiker | **Laag** — graceful degradation, geen cascading failure |

### 5.6 Elevation of Privilege (rechtenverhoging)

| # | Bedreiging | Grens | Bestaande maatregel | Restrisico |
|---|-----------|-------|-------------------|-----------|
| EP-1 | Gebruiker probeert admin-endpoints aan te roepen | 1 | `require_role(UserRole.ADMIN)` op model-switch en credits-topup | **Laag** |
| EP-2 | Gebruiker wijzigt eigen rol in de database | 2 | Geen endpoint om rollen te wijzigen; vereist directe databasetoegang | **Laag** |
| EP-3 | Gebruiker benadert andermans verkenningen/gesprekken | 1→2 | Eigendomscontrole op alle persoonlijke endpoints | **Laag** |
| EP-4 | Gratis gebruiker omzeilt dagelijkse limiet | 1 | Server-side quota-tracking per dag in `daily_usage`-tabel | **Laag** — limiet is server-side, niet te omzeilen via de client |
| EP-5 | Gebruiker met verlopen licentie blijft platform gebruiken | 1 | Licentie-validatie bij elke graph/reasoning-aanroep | **Laag** |

---

## 6. Top 5 bedreigingsscenario's

### Scenario 1: SECRET_KEY compromis (Kritiek)

**Aanvaller**: Kwaadwillende insider of aanvaller met servertoegang
**Pad**: Leest SECRET_KEY uit omgevingsvariabelen of .env-bestand
**Impact**:
- Kan JWT-tokens smeden voor elke gebruiker (volledige account-overname)
- Kan Fernet-sleutel afleiden → alle opgeslagen LLM API-keys ontsleutelen
- Kan onbeperkt LLM-kosten genereren op rekening van alle BYOK-gebruikers

**Waarschijnlijkheid**: Laag (vereist servertoegang)
**Impact**: Kritiek
**Risicoscore**: Hoog

**Aanbevolen mitigatie**:
- Aparte `ENCRYPTION_MASTER_KEY` voor KeyVault (loskoppelen van JWT-signing)
- Key-derivatie via PBKDF2 in plaats van SHA-256 (zie S13-05)
- SECRET_KEY rotatie-procedure documenteren
- Monitoring op afwijkende JWT-ondertekeningen

---

### Scenario 2: Prompt injection leidt tot misleidend beleidsadvies (Gemiddeld)

**Aanvaller**: Kwaadwillende gebruiker of geautomatiseerde aanval
**Pad**: Stuurt een zorgvuldig geformuleerde vraag die de systeemprompt omzeilt
**Impact**:
- LLM genereert beleidsadvies dat niet onderbouwd is door het causale model
- Beleidsmedewerker neemt beslissingen op basis van onbetrouwbare output
- Reputatieschade voor het platform

**Waarschijnlijkheid**: Laag–Gemiddeld (bekende patronen worden geblokkeerd; creatieve varianten blijven mogelijk)
**Impact**: Hoog
**Risicoscore**: Gemiddeld (verlaagd van Hoog door meervoudige mitigatie)

**Geïmplementeerde mitigaties** (OWASP LLM Top 10):
- ✅ **LLM01 — Prompt Injection**: `llm_guard.py` blokkeert 18 bekende injectiepatronen (NL+EN) vóór de LLM-aanroep, met audit logging
- ✅ **LLM05 — Output Handling**: `sanitize_llm_output()` neutraliseert HTML/XSS in LLM-responses
- ✅ **LLM07 — System Prompt Leakage**: Leakage-detectie + expliciete "nooit onthullen"-regel in systeemprompt
- ✅ **LLM09 — Misinformation**: `validate_response_factors()` controleert of genoemde factoren in het model voorkomen
- ✅ Antwoord-validatie actief op reasoning en wizard endpoints
- ✅ Audit logging van geblokkeerde injection- en leakage-pogingen

**Resterende aanbevelingen**:
- Disclaimer in de UI dat AI-antwoorden altijd menselijke beoordeling vereisen
- Overweeg een tweede LLM-aanroep als "validator" voor verdachte antwoorden
- Periodiek de injectiepatronen bijwerken op basis van nieuwe technieken

---

### Scenario 3: LLM-provider datalek onthult beleidsgevoelige vragen (Gemiddeld)

**Aanvaller**: Niet van toepassing — risico ligt bij de externe dienstverlener
**Pad**: OpenAI of Anthropic krijgt een datalek; gebruikersvragen worden publiek
**Impact**:
- Gevoelige beleidsvragen en -overwegingen van klanten worden openbaar
- Concurrentiepositie van klantorganisaties geschaad
- AVG-implicaties als vragen herleidbaar zijn tot personen

**Waarschijnlijkheid**: Laag (grote providers hebben uitgebreide beveiliging)
**Impact**: Hoog
**Risicoscore**: Gemiddeld

**Aanbevolen mitigatie**:
- Data Processing Agreement (DPA) met elke LLM-provider
- Privacyverklaring die uitlegt dat vragen naar externe AI-diensten worden gestuurd
- Optie voor on-premise LLM-deployment voor gevoelige klanten
- Minimaliseer persoonlijk identificeerbare informatie in prompts

---

### Scenario 4: Denial of Service via ongelimiteerde endpoints (Gemiddeld)

**Aanvaller**: Geautomatiseerd script, eventueel met gratis account
**Pad**: Stuurt duizenden verzoeken per seconde naar graph- of simulatie-endpoints
**Impact**:
- Server wordt onbeschikbaar voor alle gebruikers
- CPU-uitputting door simulatieberekeningen
- Mogelijk hoge LLM-kosten als reasoning-endpoints getroffen worden

**Waarschijnlijkheid**: Gemiddeld (eenvoudig uit te voeren)
**Impact**: Gemiddeld
**Risicoscore**: Gemiddeld

**Aanbevolen mitigatie**:
- Rate limiting uitbreiden naar alle endpoints (niet alleen auth)
- Globale limiet per gebruiker (bijv. 100 requests/minuut)
- Concurrency-limiet op simulatie-endpoints
- Reverse proxy (Caddy/nginx) met connection-rate limiting als eerste verdedigingslinie

---

### Scenario 5: Databasecompromis onthult versleutelde API-keys (Gemiddeld)

**Aanvaller**: Aanvaller met databasetoegang (via SQL-injectie, gelekte credentials, of backup-diefstal)
**Pad**: Leest `user_api_keys.encrypted_key` kolom + achterhaalt SECRET_KEY
**Impact**:
- Alle opgeslagen LLM API-keys van BYOK-gebruikers zijn te ontsleutelen
- Financiële schade voor gebruikers (ongeautoriseerd LLM-gebruik)
- Vertrouwensverlies

**Waarschijnlijkheid**: Laag (SQL-injectie onwaarschijnlijk door ORM; vereist combinatie van DB-toegang + SECRET_KEY)
**Impact**: Hoog
**Risicoscore**: Gemiddeld

**Aanbevolen mitigatie**:
- Aparte encryptiesleutel (niet afgeleid van SECRET_KEY) — zie S13-05
- Database-SSL afdwingen in productie — zie S13-05
- Reguliere key-rotatie-mogelijkheid voor gebruikers
- Monitoring op ongewoon gebruik van opgeslagen API-keys

---

## 7. Restrisico's (bewust geaccepteerd)

| # | Risico | Reden voor acceptatie |
|---|--------|----------------------|
| R-1 | `unsafe-inline` in CSP voor scripts | Vereist door Jinja2-templates met inline JavaScript. Volledige CSP met nonces zou een significante refactor vereisen. Gemitigeerd door server-side rendering en escaping. |
| R-2 | Geen e-mailverificatie bij registratie | Licentie-key fungeert als toegangscontrole. E-mailverificatie voegt complexiteit toe zonder proportioneel beveiligingsvoordeel in de huidige context (B2B met bekende klanten). |
| R-3 | Analist-rol heeft momenteel geen extra rechten | De rol is gedefinieerd maar niet gedifferentieerd. Acceptabel zolang er geen analist-specifieke endpoints zijn. Moet worden herzien zodra analytische features worden toegevoegd. |
| R-4 | Audit logs op lokaal bestandssysteem | Acceptabel voor de huidige omvang. Bij opschaling moet worden overgestapt op een centraal logsysteem (bijv. ELK-stack of CloudWatch) met tamper-detectie. |
| R-5 | LLM-prompts bevatten volledige modelcontext | Noodzakelijk voor de kernfunctionaliteit. De DAG-structuur is geen geheim (wetenschappelijk onderbouwd, niet concurrentiegevoelig). Gebruikersvragen zijn wel gevoelig — zie scenario 3. |
| R-6 | Geen multi-factor authenticatie (MFA) | Proportioneel voor de huidige gebruikersgroep (B2B beleidsmedewerkers). Bij uitbreiding naar grotere organisaties of gevoeligre domeinen moet MFA worden toegevoegd. |

---

## 8. Aanbevelingen (geprioriteerd)

### Hoge prioriteit

1. **Loskoppelen encryptiesleutel van JWT-signing** (S13-05)
   Voorkomt dat één gelekte sleutel alle beveiligingslagen doorbreekt.

2. **Rate limiting uitbreiden** naar alle endpoints
   Nu hebben slechts 3 van 39 endpoints rate limiting. Een globale limiet per gebruiker is essentieel.

3. **Prompt injection monitoring** ✅ (deels geïmplementeerd)
   LLM Guard blokkeert en logt bekende patronen. Restpunt: analyseer audit logs periodiek op nieuwe varianten.

4. **Data Processing Agreement** met LLM-providers
   Juridische bescherming voor de gegevens die naar externe diensten worden gestuurd.

### Gemiddelde prioriteit

5. **Database-SSL afdwingen** in productie (S13-05)
6. **Audit event toevoegen voor credits topup** (ontbreekt momenteel)
7. **Concurrency-limiet** op simulatie- en LLM-endpoints
8. **Disclaimer in UI** dat AI-antwoorden menselijke beoordeling vereisen

### Lage prioriteit

9. **CSP verbeteren** — `unsafe-inline` vervangen door nonces (significante refactor)
10. **Centraal logsysteem** bij opschaling
11. **MFA-optie** bij uitbreiding naar grotere organisaties

---

## 9. Relatie met bestaande maatregelen

Dit threat model bouwt voort op de beveiligingsaudit (`docs/beveiligingsaudit-v2.md`) die alle 23 bevindingen heeft geadresseerd via EPIC-11. De onderstaande tabel toont hoe de STRIDE-bedreigingen zich verhouden tot de eerder geïmplementeerde maatregelen:

| STRIDE-categorie | Relevante EPIC-11 stories | Status |
|-----------------|--------------------------|--------|
| Spoofing | S11-01 (bcrypt, refresh tokens, wachtwoordbeleid) | ✅ Geïmplementeerd |
| Tampering | S11-02 (CSRF, input-validatie, CSP) | ✅ Geïmplementeerd |
| Repudiation | S11-04 (auditlogging) | ✅ Geïmplementeerd |
| Information Disclosure | S11-04 (generieke foutmeldingen), S11-02 (SRI) | ✅ Geïmplementeerd |
| Denial of Service | S11-01 (rate limiting op auth) | ⚠️ Gedeeltelijk — alleen auth-endpoints |
| Elevation of Privilege | S11-03 (RBAC, UUIDs, resource-isolatie) | ✅ Geïmplementeerd |

---

## 10. Herziening

Dit threat model moet worden herzien bij:

- Toevoegen van nieuwe actoren (bijv. API-consumenten, webhook-integraties)
- Wijzigingen in de architectuur (bijv. microservices, message queues)
- Nieuw domeinmodel dat gevoeliger data bevat (bijv. gezondheidszorg)
- Na een beveiligingsincident
- Minimaal jaarlijks, ongeacht wijzigingen
