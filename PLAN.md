# Graaf Zeppelin — Causal Reasoning Platform voor Sportdeelname

## Visie
Een webapplicatie die sportprofessionals (bonden, gemeenten, clubs) toegang geeft
tot een graph-based causaal model (DAG) waarmee ze — via hun eigen LLM — betrouwbaar
en herhaalbaar kunnen redeneren over sportdeelname in hun domein.

## Kernprincipes
1. **Model blijft server-side** — de DAG wordt nooit als bestand gedistribueerd
2. **Gebruiker koppelt eigen LLM** — via API key (OpenAI, Anthropic, etc.)
3. **Licentie = toegang** — geen geldige licentie = geen API-toegang
4. **Herhaalbare output** — de DAG constraineert het LLM, niet andersom

---

## Architectuur

```
┌─────────────────────────┐
│     Web Frontend        │
│     (Jinja2 + HTMX)     │ ◄── Simpel, snel, geen JS-framework nodig
│                         │     voor niet-technische doelgroep
│  • DAG visualisatie     │
│  • Query interface      │
│  • Licentie dashboard   │
│  • Release notes        │
└────────┬────────────────┘
         │ HTTP
┌────────▼────────────────┐
│     FastAPI Backend      │
│                         │
│  /api/auth    → login, license check
│  /api/graph   → DAG query, visualisatie
│  /api/reason  → LLM reasoning via DAG
│  /api/releases → release notes, versies
│                         │
│  Core:                  │
│  • DAGEngine    — graph ops, pad-analyse
│  • PromptBuilder — DAG → LLM prompt
│  • LicenseManager — key validatie
│  • ReleaseManager — versioning, migratie
└────────┬────────────────┘
         │
┌────────▼────────────────┐
│     SQLite / PostgreSQL  │
│                         │
│  • users & licenses     │
│  • DAG models (versioned)│
│  • reasoning sessions   │
│  • release history      │
└─────────────────────────┘
```

## Waarom Jinja2 + HTMX (geen React)?
- Doelgroep is niet-technisch → simpelheid > complexiteit
- Geen build pipeline nodig → snellere ontwikkeling
- HTMX geeft SPA-achtig gedrag zonder JavaScript-framework
- Minder onderhoudslast op lange termijn
- Graph visualisatie via server-rendered SVG of D3.js widget

---

## Componenten

### 1. DAG Engine (`core/dag_engine.py`)
- Laadt causale graaf (nodes = factoren, edges = causale relaties)
- Ondersteunt queries: "welke factoren beïnvloeden X?"
- Pad-analyse: "wat is het causale pad van A naar B?"
- Interventie-simulatie: "wat als we factor X met 20% verbeteren?"
- Graaf representatie: NetworkX (Python)

### 2. Prompt Builder (`core/prompt_builder.py`)
- Vertaalt DAG-paden naar gestructureerde LLM-prompts
- Zorgt voor herhaalbaarheid: zelfde graph + zelfde query = zelfde prompt
- Injecteert domeincontext (sportdeelname terminologie)
- Ondersteunt templates per use case

### 3. LLM Connector (`core/llm_connector.py`)
- Gebruiker koppelt eigen API key (encrypted opgeslagen)
- Ondersteunt OpenAI, Anthropic, lokale modellen (Ollama)
- Rate limiting per licentie-tier
- Response caching voor identieke queries

### 4. License Manager (`core/license_manager.py`)
- Licentie per organisatie (bond, gemeente, club)
- Tiers: basis, professional, enterprise
- Online validatie bij elke sessie
- Usage tracking (queries per maand)
- Geen offline modus = geen model kopiëren

### 5. Release Manager (`core/release_manager.py`)
- Semantic versioning voor DAG-model
- Release notes bij elke update
- **Trendbreuk-preventie**: major releases krijgen:
  - Migratieguide
  - Parallelle draaiperiode (oud + nieuw model)
  - Vergelijkingsrapport (output oud vs nieuw)
- Automatische notificatie aan gebruikers

---

## Data Model — Sportdeelname DAG

Voorbeeldnodes (factoren):
- Bereikbaarheid faciliteiten
- Kwaliteit begeleiding/coaching
- Kosten deelname
- Sociaal netwerk / vriendengroep
- Aanbod / programmering
- Veiligheid & inclusie
- Tijd/agenda beschikbaarheid

Voorbeeldrelaties:
- Bereikbaarheid → Sportdeelname (positief, sterk)
- Kosten → Sportdeelname (negatief, matig)
- Sociaal netwerk → Motivatie → Sportdeelname (indirect)

---

## Projectstructuur

```
Graaf_Zeppelin/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI applicatie
│   ├── config.py               # Settings & env vars
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py             # Login, registratie
│   │   ├── license.py          # Licentie-endpoints
│   │   ├── graph.py            # DAG query endpoints
│   │   ├── reasoning.py        # LLM reasoning endpoints
│   │   └── releases.py         # Release notes endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── dag_engine.py       # Graph engine (NetworkX)
│   │   ├── prompt_builder.py   # DAG → LLM prompt
│   │   ├── llm_connector.py    # Multi-provider LLM client
│   │   ├── license_manager.py  # Licentie logica
│   │   └── release_manager.py  # Versioning & release notes
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # SQLAlchemy models
│   │   ├── license.py
│   │   ├── graph.py
│   │   └── release.py
│   ├── templates/              # Jinja2 templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── graph_viewer.html
│   │   ├── reasoning.html
│   │   ├── releases.html
│   │   └── license.html
│   └── static/
│       ├── css/
│       ├── js/                 # Minimale JS (HTMX + D3)
│       └── img/
├── data/
│   └── models/                 # DAG model bestanden (JSON)
│       └── sportdeelname_v1.json
├── tests/
│   ├── test_dag_engine.py
│   ├── test_prompt_builder.py
│   ├── test_license.py
│   └── test_api.py
├── alembic/                    # DB migraties
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Fasering

### Fase 1 — Fundament
- [x] Projectstructuur opzetten
- [x] DAG engine met NetworkX (v1+v2, 562 regels, 33 tests)
- [x] Voorbeeld sportdeelname model (v1: 15 factoren + v2.3.0: 69 factoren)
- [x] FastAPI met basisroutes (12+ endpoints)
- [x] Jinja2 templates met HTMX
- [x] Licentie-check (basis)
- [x] SQLite database setup (async SQLAlchemy)

### Fase 2 — LLM Integratie
- [x] Prompt builder (DAG → prompt, 4 templates, 6 constraints)
- [x] LLM connector (OpenAI / Anthropic, BYOK)
- [x] Query interface in frontend
- [ ] Response caching

### Fase 3 — Productie-ready
- [x] Robuuste licentie-manager met tiers (basis/professional/enterprise)
- [x] Release notes systeem (semantic versioning, migratieguides)
- [ ] Trendbreuk-detectie & migratie tooling
- [ ] PostgreSQL migratie
- [ ] Docker deployment
- [ ] Monitoring & logging

### Fase 4 — Uitbreiding
- [ ] Obsidian Publish content integratie
- [ ] Meerdere domeinmodellen
- [ ] API voor externe integraties
- [ ] Export: rapporten, presentaties
