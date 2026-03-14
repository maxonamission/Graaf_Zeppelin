# Graaf Zeppelin — Beleidsverkenner voor Sportdeelname

## Product

Een webapplicatie waarmee beleidsmedewerkers van sportbonden, gemeenten en clubs
beleid kunnen verkennen en interventies kunnen doorrekenen. De app gebruikt een
extern aangeleverd causaal model (DAG) als redeneerstructuur en combineert dit met
LLM-integratie voor natuurlijke taal interactie.

### Scope-afbakening

| Onderdeel | Rol | Verantwoordelijkheid |
|-----------|-----|----------------------|
| **App** (`app/`) | Het product | Wordt hier ontwikkeld |
| **Causaal model** (`data/models/`) | Externe input | Wordt separaat ontwikkeld; de app laadt het model as-is |
| **Conversie-tools** (`graaf_zeppelin/`) | Developer tooling | Hulpmiddelen voor de modelontwikkelaar; niet nodig in de app |

### Doelgroep

Beleidsmedewerkers bij sportbonden, gemeenten en clubs die:
- Geen technische achtergrond hebben
- Willen begrijpen welke factoren sportdeelname beïnvloeden
- Interventies willen verkennen ("wat als we meer investeren in coaching?")
- Onderbouwde beleidsadviezen nodig hebben

### Kernprincipes

1. **Model as-is** — de app laadt het causaal model zonder het te wijzigen
2. **Gebruiker koppelt eigen LLM** — via API key (OpenAI, Anthropic)
3. **Licentie = toegang** — geen geldige licentie = geen API-toegang
4. **Herhaalbare output** — de DAG constraineert het LLM, niet andersom
5. **Eenvoud voor de gebruiker** — geen technische kennis nodig

---

## Architectuur

```
┌─────────────────────────────┐
│     Web Frontend             │
│     (Jinja2 + HTMX + D3)    │ ◄── Simpel, geen JS-framework
│                              │
│  • Beleidsverkenner          │     Doelgroep is niet-technisch
│  • Interventie-simulator     │
│  • AI-assistent (chat)       │
│  • Dashboard & licentie      │
└────────────┬────────────────┘
             │ HTTP
┌────────────▼────────────────┐
│     FastAPI Backend          │
│                              │
│  /api/graph    → model verkennen, simuleren
│  /api/reasoning → LLM-redenering
│  /api/auth     → login, registratie
│  /api/license  → licentie & quota
│  /api/releases → release notes
│                              │
│  Core:                       │
│  • DAGEngine      — graph laden & queries
│  • SliderEngine   — interventie-simulatie
│  • PromptBuilder  — DAG → LLM prompt
│  • LLMConnector   — multi-provider client
│  • LicenseManager — licentie & quota
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│     Causaal Model (extern)   │
│     data/models/*.json       │
│                              │
│  Wordt as-is geladen.        │
│  Separaat ontwikkeld.        │
└─────────────────────────────┘
```

---

## Bestaande componenten

### Gebouwd en werkend

| Component | Module | Status | Tests |
|-----------|--------|--------|-------|
| DAG Engine | `core/dag_engine.py` | ✅ Volledig (v1+v2 schema, queries, simulatie) | 33 |
| Slider Engine | `core/slider_engine.py` | ✅ Volledig (3 curvemodellen, multi-slider) | 12 |
| Prompt Builder | `core/prompt_builder.py` | ✅ Volledig (4 templates, 6 constraints, NL) | 7 |
| LLM Connector | `core/llm_connector.py` | ✅ Volledig (OpenAI, Anthropic, BYOK) | — |
| License Manager | `core/license_manager.py` | ✅ Volledig (3 tiers, quota, key-generatie) | — |
| Auth | `core/auth.py` | ✅ Volledig (JWT, wachtwoordhashing) | — |
| Release Manager | `core/release_manager.py` | ✅ Volledig (versioning, migratieguides) | — |
| Graph API | `api/graph.py` | ✅ 12 endpoints (factoren, relaties, paden, sliders, simulatie) | — |
| Reasoning API | `api/reasoning.py` | ✅ 2 endpoints (query, interventie) | — |
| Frontend | `templates/` + `static/` | ✅ 8 pagina's (dashboard, graph, chat, licentie, etc.) | — |
| API Tests | `tests/test_api.py` | ⚠️ 7 tests, async fixture-probleem | 0/7 |

### Nog niet gebouwd

| Component | Prioriteit | Toelichting |
|-----------|------------|-------------|
| Begeleide beleidsverkenning | Hoog | Workflow: vraag → relevante sliders → kwalificatie → simulatie → advies |
| Slider-kwalificatievragen UX | Hoog | Vertaling van abstracte sliderwaarden naar begrijpelijke vragen |
| API-tests fixen | Hoog | 7 tests falen door async fixture-probleem; API-laag heeft geen werkende testdekking |
| Tests voor core modules | Hoog | LLM Connector, License Manager, Auth en Release Manager missen dedicated tests |
| Interventie-rapportage | Midden | Export of samenvatting van simulatieresultaten |
| Onboarding flow | Midden | Eerste-gebruik uitleg voor niet-technische gebruikers |
| Error handling & feedback | Midden | Duidelijke meldingen bij fouten, limieten, model-beperkingen |
| Docker deployment | Laag | Containerisatie voor productie |
| Monitoring & logging | Laag | Observability voor productie |

---

## Fasering

### Fase 1 — Beleidsverkenner werkend maken ← **huidige focus**

De kern van het product: een beleidsmedewerker kan beleid verkennen en interventies doorrekenen.

- [ ] **Begeleide interventie-flow**: gebruiker stelt beleidsvraag → app bepaalt relevante sliders → stelt kwalificatievragen → simuleert → toont resultaat met uitleg
- [ ] **Slider-kwalificatie UX**: de 16 kwalificatievragen (2 per slider) presenteren als begrijpelijke multiple-choice in de interface
- [ ] **Resultaatpagina**: simulatie-uitkomsten tonen als leesbaar overzicht (welke factoren worden beïnvloed, hoe sterk, via welk pad)
- [ ] **Graph viewer verbeteren**: kleur-codering op domein, hover-info met factorbeschrijving, visuele markering van interventie-effecten
- [ ] **Dashboard aanscherpen**: snelkoppelingen naar meest relevante acties (verken, simuleer, vraag AI)

### Fase 2 — AI-assistent bruikbaar maken

De LLM-integratie moet naadloos werken voor niet-technische gebruikers.

- [ ] **Voorbeeldvragen aanbieden**: klikbare suggesties die de gebruiker op weg helpen
- [ ] **Factor-selectie vereenvoudigen**: automatisch relevante factoren selecteren op basis van de vraag (niet handmatig aanvinken)
- [ ] **Antwoord-kwaliteit borgen**: response valideren tegen model (zijn genoemde factoren echt in het model?)
- [ ] **Sessie-geschiedenis**: eerdere vragen en antwoorden terugzien
- [ ] **Foutafhandeling LLM**: duidelijke melding bij API-fout, rate limit, ongeldige key

### Fase 3 — Stabiliteit & kwaliteit

- [ ] API-tests fixen (async fixture-probleem in `test_api.py`) — **hoge prioriteit**, API-laag is ongetest
- [ ] Tests toevoegen voor core modules zonder dedicated tests (LLM Connector, License Manager, Auth, Release Manager)
- [ ] Integratietests toevoegen (volledige flow: login → verken → simuleer → AI-vraag)
- [ ] Error handling en gebruikersfeedback verbeteren
- [ ] README.md bijwerken naar productfocus (beleidsverkenner, niet platform-beschrijving)
- [ ] Onboarding: eerste-gebruik uitleg of korte tutorial

### Fase 4 — Productie & uitbreiding

- [ ] Docker deployment
- [ ] PostgreSQL migratie (productie-database)
- [ ] Monitoring & logging
- [ ] Interventie-rapportage: PDF/Markdown export van simulatieresultaten
- [ ] Meerdere modellen ondersteunen (niet alleen sportdeelname)
