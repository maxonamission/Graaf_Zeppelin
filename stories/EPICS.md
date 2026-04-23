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
| [S05-04](done/S05-04-graph-viewer-verbeteren.md) | ✅ Done | Graph viewer verbeteren (domeinkleur, hover, model-selector) |
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
Beoordeeld conform OWASP Top 10 (2021), CWE/SANS Top 25, OWASP ASVS v4.0, en OWASP Top 10 for LLM Applications.
Zie: `docs/beveiligingsaudit-v2.md` voor het volledige auditrapport.

| Story | Status | Prioriteit | Beschrijving |
|-------|--------|------------|-------------|
| [S11-01](done/S11-01-authenticatie-hardening.md) | ✅ Done | KRITIEK | Authenticatie hardening (bcrypt, refresh-tokens, wachtwoordcomplexiteit, SECRET_KEY) |
| [S11-02](done/S11-02-api-bescherming.md) | ✅ Done | KRITIEK/HOOG | API-bescherming (input validatie, CSRF, security headers, XSS-fix, SRI) |
| [S11-03](done/S11-03-autorisatie-verbeteren.md) | ✅ Done | HOOG | Autorisatie & toegangscontrole (RBAC enum, per-user model, UUIDs) |
| [S11-04](done/S11-04-logging-monitoring.md) | ✅ Done | GEMIDDELD | Beveiligingslogging & monitoring (structured audit logger, generieke errors) |
| [S11-05](done/S11-05-geautomatiseerde-security-checks.md) | ✅ Done | LAAG | Geautomatiseerde security checks (bandit, pip-audit, CI workflow) |
| [S11-06](done/S11-06-llm-guard-patronen-externaliseren.md) | ✅ Done | GEMIDDELD | LLM Guard patronen externaliseren naar configureerbaar JSON |
| [S11-07](done/S11-07-guard-analyst-post-hoc-analyse.md) | ✅ Done | GEMIDDELD | Guard Analyst: post-hoc analyse van geblokkeerde queries via LLM |

---

### EPIC-12: Multi-domein ondersteuning ✅

De app domein-agnostisch maken zodat dezelfde codebase kan worden ingezet voor
elk causaal model (sportdeelname, vitale vereniging, gezondheidszorg, etc.)
zonder codewijzigingen — alleen een ander model-JSON.

| Story | Status | Prioriteit | Beschrijving |
|-------|--------|------------|-------------|
| [S12-01](done/S12-01-dag-engine-domein-agnostisch.md) | ✅ Done | HOOG | DAG Engine domein-agnostisch (dynamische veldnamen in parser) |
| [S12-02](done/S12-02-systeemprompts-parametriseren.md) | ✅ Done | HOOG | Systeemprompts parametriseren (domeinnaam uit model-metadata) |
| [S12-03](done/S12-03-voorbeeldvragen-uit-model.md) | ✅ Done | HOOG | Voorbeeldvragen uit model-metadata laden (templates dynamisch) |
| [S12-04](done/S12-04-app-metadata-configureerbaar.md) | ✅ Done | GEMIDDELD | App-metadata configureerbaar (titel, beschrijving, intro) |
| [S12-05](done/S12-05-meertalige-mappings.md) | ✅ Done | GEMIDDELD | Polarity/strength mappings meertalig (NL + EN) |
| [S12-06](done/S12-06-model-metadata-schema.md) | ✅ Done | HOOG | Model-metadata schema uitbreiden (persona, voorbeeldvragen, taal) |

---

### EPIC-13: Beveiligingsvervolg — van audit naar doorlopend proces 🔲

De beveiligingsaudit (EPIC-11) heeft alle technische kwetsbaarheden aangepakt op basis van
OWASP Top 10 en CWE/SANS Top 25. EPIC-13 adresseert de strategische vervolgstappen die
nodig zijn voor een volledige beveiligingsstrategie: threat modeling, incident response,
penetratietests, en een doorlopend review-proces.

| Story | Status | Prioriteit | Beschrijving |
|-------|--------|------------|-------------|
| [S13-01](done/S13-01-threat-model.md) | ✅ Done | HOOG | Threat model opstellen (STRIDE, actoren, vertrouwensgrenzen) |
| [S13-02](backlog/S13-02-incident-response-plan.md) | 🔲 Backlog | HOOG | Incident response plan (classificatie, escalatie, communicatie) |
| [S13-03](backlog/S13-03-penetratietest.md) | 🔲 Backlog | HOOG | Penetratietest plannen en uitvoeren (onafhankelijke validatie) |
| [S13-04](backlog/S13-04-dependency-lifecycle.md) | 🔲 Backlog | GEMIDDELD | Dependency lifecycle management (Dependabot, SLA, lock-file) |
| [S13-05](backlog/S13-05-keyvault-hardening.md) | 🔲 Backlog | GEMIDDELD | KeyVault en cryptografie hardening (PBKDF2, database-SSL) |
| [S13-06](backlog/S13-06-security-review-proces.md) | 🔲 Backlog | GEMIDDELD | Structureel security review proces (checklist, jaarplanning, champion) |

---

### EPIC-14: Graph-methodologie afstemming (OS-actieplan) 🔲

Afstemmen van Graaf Zeppelin op de gedeelde graph-methodologie (acht conventies +
appendix tijdsdimensie) vanuit Codebase-Olympus. Repareert twee structurele
inconsistenties (FEEDBACK-edges vs. globale acyclic-check, `time_lag` als dead field),
introduceert Pydantic-modellen, een invarianten-catalogus, leesbare IDs, en tilt de
ontwikkelstraat op Olympus-niveau.

Bron: `docs/actieplan-os.md` (overgenomen vanuit `maxonamission/Codebase-Olympus`).

**Genomen beleidskeuzes (zie actieplan §"Open beleidskeuzes"):**
1. **`time_lag`** — Pad B (schrappen) nu, Pad A (iteratieve-tikken-simulatie) op roadmap als eigen epic
2. **ID-schema** — direct integraal migreren naar leesbaar schema (Vorm A: `{DOMEIN-AFK}-{NIVEAU}-{VOLGNR}`); geen externe consumenten, dus geen compatibiliteitslaag nodig; volledige per-node-review van de mapping. Afkortingen-tabel en L12-conventie vastgelegd in S14-05.
3. **`knowledge_graph.py`** — consolideren met Pydantic-`Graph`-model in `app/core/`; standalone module verwijderd of dunne wrapper

**Follow-up buiten deze epic:** uniforme kenmerken-taxonomie voor graph-objecten
(nodes én edges), cross-project met Codebase-Olympus. Vastgelegd als wens in
[`docs/uniforme-kenmerken-taxonomie.md`](../docs/uniforme-kenmerken-taxonomie.md).
Niet blokkerend voor uitvoering van S14-01..S14-07; hoort thuis in een
Olympus-conversatie en uiteindelijk in `docs/graph-methodology.md` bij Olympus.

**Kritisch pad:** S14-01 → S14-02 → S14-04 → S14-05. S14-03 is triviaal (~1u) zodra
S14-02 staat. S14-07 kan parallel (alleen docs).

| Story | Status | Prioriteit | Beschrijving |
|-------|--------|------------|-------------|
| [S14-01](backlog/S14-01-cycle-check-per-edge-type.md) | 🔲 Backlog | HOOG | Cycle-check per edge-type (GZ-01) — FEEDBACK-edges mogen cyclisch zijn |
| [S14-02](backlog/S14-02-pydantic-graph-models.md) | 🔲 Backlog | HOOG | Pydantic-modellen voor Node en Edge + consolidatie `knowledge_graph.py` (GZ-02) |
| [S14-03](backlog/S14-03-time-lag-beslissing.md) | 🔲 Backlog | GEMIDDELD | `time_lag` schrappen (Pad B); Pad A op roadmap (GZ-03) |
| [S14-04](backlog/S14-04-invarianten-catalogus.md) | 🔲 Backlog | HOOG | Invarianten-catalogus: cycle/orphan/duplicate/dangling + CLI (GZ-04) |
| [S14-05](backlog/S14-05-id-schema-herontwerp.md) | 🔲 Backlog | GEMIDDELD | ID-schema integrale migratie (GZ-05) |
| [S14-06](backlog/S14-06-ontwikkelstraat.md) | 🔲 Backlog | GEMIDDELD | Ontwikkelstraat parallel aan Olympus: ruff, mypy, pre-commit, CI, hooks, stories (GZ-06) |
| [S14-07](backlog/S14-07-schema-evolutie-doc.md) | 🔲 Backlog | LAAG | Schema-evolutie v1→v2 documenteren als methodologie-bijdrage (GZ-07) |
