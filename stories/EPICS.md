# Epics — Graaf Zeppelin Beleidsverkenner

Overzicht van alle epics. Elke epic heeft stories in `backlog/`, `doing/` of `done/`.

## Status-legenda

| Map | Betekenis |
|-----|-----------|
| `done/` | Afgerond en werkend |
| `doing/` | In ontwikkeling |
| `backlog/` | Gepland, nog niet gestart |

---

## Epics

### EPIC-01: Causaal model laden & verkennen ✅

De app kan het extern aangeleverde causaal model laden en de gebruiker laten verkennen
(factoren, relaties, domeinen, paden).

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S01-01](done/S01-01-dag-engine.md) | ✅ Done | DAG Engine — model laden, queries, pad-analyse |
| [S01-02](done/S01-02-graph-api.md) | ✅ Done | Graph API — 12 REST endpoints |
| [S01-03](done/S01-03-graph-viewer.md) | ✅ Done | Graph viewer — D3 visualisatie in frontend |

---

### EPIC-02: Interventie-simulatie met sliders ✅

Beleidsmedewerkers kunnen interventies doorrekenen via de 8 beleidssliders
met 3 wiskundige curvemodellen.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S02-01](done/S02-01-slider-engine.md) | ✅ Done | Slider Engine — 3 curvemodellen, multi-slider simulatie |
| [S02-02](done/S02-02-slider-api.md) | ✅ Done | Slider API — endpoints voor sliders, kwalificatie, simulatie |
| [S02-03](done/S02-03-slider-qualifiers-technisch.md) | ✅ Done | Kwalificatievragen — technische infrastructuur (API, JSON-schema) |

---

### EPIC-03: AI-assistent (LLM-integratie) ✅

Gebruikers kunnen in natuurlijke taal vragen stellen over het causale model.
De DAG constraineert het LLM-antwoord.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S03-01](done/S03-01-prompt-builder.md) | ✅ Done | Prompt Builder — 4 templates, 6 constraints, NL |
| [S03-02](done/S03-02-llm-connector.md) | ✅ Done | LLM Connector — OpenAI, Anthropic, BYOK |
| [S03-03](done/S03-03-reasoning-api.md) | ✅ Done | Reasoning API — query & interventie endpoints |
| [S03-04](done/S03-04-chat-frontend.md) | ✅ Done | Chat interface — frontend met factorselectie |

---

### EPIC-04: Authenticatie & licenties ✅

Gebruikers moeten inloggen met een geldige licentie. Tiers bepalen quota.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S04-01](done/S04-01-auth.md) | ✅ Done | Auth — JWT, wachtwoordhashing, login/registratie |
| [S04-02](done/S04-02-license-manager.md) | ✅ Done | License Manager — 3 tiers, quota, key-generatie |
| [S04-03](done/S04-03-frontend-auth.md) | ✅ Done | Frontend — dashboard, licentiepagina |

---

### EPIC-05: Begeleide beleidsverkenning ✅

De kernervaring: een beleidsmedewerker stelt een beleidsvraag en wordt begeleid
naar een onderbouwd advies via kwalificatievragen en simulatie.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S05-01](done/S05-01-interventie-flow.md) | ✅ Done | Begeleide interventie-flow (opslaan & laden verkenningen) |
| [S05-02](done/S05-02-slider-kwalificatie-ux.md) | ✅ Done | Slider-kwalificatie UX (voortgang, feedback) |
| [S05-03](done/S05-03-resultaatpagina.md) | ✅ Done | Resultaatpagina (stats, filters, impact-balken) |
| [S05-04](done/S05-04-graph-viewer-verbeteren.md) | ✅ Done | Graph viewer verbeteren (kleurcodering, hover, zoom) |
| [S05-05](done/S05-05-dashboard-aanscherpen.md) | ✅ Done | Dashboard aanscherpen (domeinoverzicht, verkenningen) |

---

### EPIC-06: AI-assistent bruikbaar maken ✅

De LLM-integratie naadloos laten werken voor niet-technische gebruikers.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S06-01](done/S06-01-voorbeeldvragen.md) | ✅ Done | Voorbeeldvragen aanbieden |
| [S06-02](done/S06-02-auto-factor-selectie.md) | ✅ Done | Automatische factor-selectie |
| [S06-03](done/S06-03-antwoord-validatie.md) | ✅ Done | Antwoord-kwaliteit borgen |
| [S06-04](done/S06-04-sessie-geschiedenis.md) | ✅ Done | Sessie-geschiedenis |
| [S06-05](done/S06-05-foutafhandeling-llm.md) | ✅ Done | Foutafhandeling LLM |

---

### EPIC-07: Businessmodel & toegang ✅

Prijsmodel en toegangsstructuur voor de beleidsverkenner.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S07-01](done/S07-01-gratis-vragen.md) | ✅ Done | Gratis vragen (2 per dag, free-tier enforcing) |
| [S07-02](done/S07-02-betaald-account.md) | ✅ Done | Betaald account met keuze (tier vergelijking) |
| [S07-03](done/S07-03-credits-systeem.md) | ✅ Done | Credits-systeem (vast + flexibel quotum) |
| [S07-04](done/S07-04-eigen-llm-optie.md) | ✅ Done | Eigen LLM-optie (BYOK met auto-fill keys) |

---

### EPIC-08: Slider-kwalificatievragen validatie 🔲

Inhoudelijke validatie van de kwalificatievragen door domeinexperts en gebruikers.
(Zie ook: `docs/epic_slider_qualifiers.md` voor technische context.)

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S08-01](backlog/S08-01-inhoudelijke-review.md) | 🔲 Backlog | Inhoudelijke review per slider |
| [S08-02](backlog/S08-02-waarde-mapping-validatie.md) | 🔲 Backlog | Waarde-mapping validatie |
| [S08-03](backlog/S08-03-discipline-specifiek.md) | 🔲 Backlog | Discipline-specifieke vragen |
| [S08-04](backlog/S08-04-relevantie-filtering.md) | 🔲 Backlog | Relevantiefiltering optimalisatie |
| [S08-05](backlog/S08-05-gebruikerstest.md) | 🔲 Backlog | Gebruikerstest met sportbondmedewerkers |

---

### EPIC-09: Stabiliteit & kwaliteit ✅

Testdekking, error handling en documentatie op productieniveau brengen.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S09-01](done/S09-01-api-tests-fixen.md) | ✅ Done | API-tests fixen en uitbreiden (22 API tests) |
| [S09-02](done/S09-02-core-module-tests.md) | ✅ Done | Tests voor core modules (auth, license, llm, release) |
| [S09-03](done/S09-03-integratietests.md) | ✅ Done | Integratietests (register → login → explore → simulate → AI) |
| [S09-04](done/S09-04-error-handling.md) | ✅ Done | Error handling & feedback |
| [S09-05](done/S09-05-readme-update.md) | ✅ Done | README.md bijwerken naar productfocus |
| [S09-06](done/S09-06-onboarding.md) | ✅ Done | Onboarding flow (3-staps wizard) |

---

### EPIC-10: Productie & deployment ✅

Deployment, monitoring en uitbreidingen voor productiegebruik.

| Story | Status | Beschrijving |
|-------|--------|-------------|
| [S10-01](done/S10-01-docker.md) | ✅ Done | Docker deployment |
| [S10-02](done/S10-02-postgresql.md) | ✅ Done | PostgreSQL migratie (+ Alembic) |
| [S10-03](backlog/S10-03-monitoring.md) | 🔲 Backlog | Monitoring & logging |
| [S10-04](done/S10-04-export.md) | ✅ Done | Interventie-rapportage export |
| [S10-05](done/S10-05-multi-model.md) | ✅ Done | Meerdere modellen ondersteunen |

---

### EPIC-11: Beveiliging ✅

Beveiligingsaudit en hardening vóór productie-deployment.
Beoordeeld conform OWASP Top 10 (2021), CWE/SANS Top 25, OWASP ASVS v4.0.
Zie: `docs/beveiligingsaudit-v2.md` voor het volledige auditrapport.

| Story | Status | Prioriteit | Beschrijving |
|-------|--------|------------|-------------|
| [S11-01](done/S11-01-authenticatie-hardening.md) | ✅ Done | KRITIEK | Authenticatie hardening (bcrypt, secure cookies, rate limiting, JWT validatie) |
| [S11-02](done/S11-02-api-bescherming.md) | ✅ Done | KRITIEK/HOOG | API-bescherming (input validatie, CSRF, security headers, XSS-fix) |
| [S11-03](done/S11-03-autorisatie-verbeteren.md) | ✅ Done | HOOG | Autorisatie & toegangscontrole (admin-only topup/switch) |
| [S11-04](done/S11-04-logging-monitoring.md) | ✅ Done | GEMIDDELD | Beveiligingslogging & monitoring (structured audit logger) |
| [S11-05](done/S11-05-geautomatiseerde-security-checks.md) | ✅ Done | LAAG | Geautomatiseerde security checks (bandit, pip-audit script) |
