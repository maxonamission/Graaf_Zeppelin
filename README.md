# Graaf Zeppelin — Beleidsverkenner voor Sportdeelname

Een webapplicatie waarmee beleidsmedewerkers van sportbonden, gemeenten en clubs
beleid kunnen verkennen en interventies kunnen doorrekenen. De app combineert een
wetenschappelijk onderbouwd causaal model (DAG) met LLM-integratie, zodat
niet-technische gebruikers in natuurlijke taal vragen kunnen stellen over
sportbeleid en onderbouwde antwoorden krijgen.

## Wat kan een gebruiker?

- **Beleid verkennen** — Bekijk welke factoren sportdeelname beinvloeden en hoe ze
  samenhangen via een interactieve grafiekviewer
- **Interventies simuleren** — Pas beleidssliders aan en zie welke factoren worden
  beinvloed (bijv. "Wat als we investeren in betere accommodaties?")
- **Vragen stellen aan de AI** — Stel beleidsvragen in natuurlijke taal en krijg
  antwoorden die zijn gegrond in het causale model
- **Kwalificatievragen beantwoorden** — De app stelt gerichte vragen om de juiste
  sliderwaarden te bepalen voor jouw situatie

## Scope

| Onderdeel | Rol | Toelichting |
|-----------|-----|-------------|
| **App** (`app/`) | Het product | Webapplicatie met API en frontend |
| **Causaal model** (`data/models/`) | Externe input | Wordt separaat ontwikkeld; de app laadt het model as-is |
| **Conversie-tools** (`scripts/convert_graph.py`) | Developer tooling | JSON ↔ GEXF ↔ Markdown voor de modelontwikkelaar |

## Installatie

```bash
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin
pip install -r requirements.txt

# Start de applicatie
uvicorn app.main:app --reload
```

Open `http://localhost:8000` in je browser. API-documentatie: `http://localhost:8000/docs`.

### Vereisten

- Python 3.11+
- Packages: zie `requirements.txt` (FastAPI, SQLAlchemy, NetworkX, httpx, etc.)

## Hoe werkt het?

```
┌─────────────────────────────┐
│     Web Frontend             │
│     (Jinja2 + HTMX + D3)    │    Geen JS-framework nodig
│                              │
│  • Beleidsverkenner          │    Doelgroep: niet-technische
│  • Interventie-simulator     │    beleidsmedewerkers
│  • AI-assistent (chat)       │
│  • Dashboard & licentie      │
└────────────┬────────────────┘
             │ HTTP
┌────────────▼────────────────┐
│     FastAPI Backend          │
│                              │
│  /api/graph     → model verkennen, sliders, simulatie
│  /api/reasoning → LLM-redenering (BYOK)
│  /api/auth      → login, registratie
│  /api/license   → licentie & quota
└────────────┬────────────────┘
             │
┌────────────▼────────────────┐
│     Causaal Model (extern)   │
│     data/models/*.json       │
│                              │
│  69 factoren, 108 relaties   │
│  8 beleidssliders            │
│  9 domeinen                  │
└─────────────────────────────┘
```

### Kernprincipes

1. **Model as-is** — de app laadt het causaal model zonder het te wijzigen
2. **Gebruiker koppelt eigen LLM** — via API key (OpenAI, Anthropic)
3. **Licentie = toegang** — geen geldige licentie = geen API-toegang
4. **Herhaalbare output** — de DAG constraineert het LLM, niet andersom
5. **Eenvoud voor de gebruiker** — geen technische kennis nodig
6. **LLM-beveiliging** — OWASP LLM Top 10 mitigaties (prompt injection guard, output sanitisatie, leakage-detectie)

### Edge-types en cycli

Het v2-schema onderscheidt vijf edge-types. De cycle-detectie werkt **per
edge-type**, niet over de hele graph:

- **`STRUCTURAL`, `MEDIATING`, `MODERATOR`** — deze edges vormen samen een echte
  DAG; cycli worden geweigerd bij het laden (`ACYCLIC_EDGE_TYPES` in
  `app/core/dag_engine.py`).
- **`FEEDBACK`, `SOCIAL_REGULATORY`** — semantisch cyclisch (terugkoppeling,
  sociale regulatie) en daarom uitgesloten van de acycliciteit-constraint; A↔B
  is toegestaan.

Deze splitsing houdt het schema en het runtime-gedrag consistent: een
`FEEDBACK`-edge in de data werkt ook echt als feedback, in plaats van door de
globale DAG-check te worden afgewezen.

## Projectstructuur

```
app/
  main.py                 # FastAPI app, graph caching bij startup
  config.py               # Instellingen (model path, DB, secrets)
  api/
    graph.py              # Graph & slider endpoints
    reasoning.py          # LLM-redenering met foutafhandeling
    auth.py               # Registratie & login
    deps.py               # Gedeelde dependencies (auth, graph)
  core/
    dag_engine.py         # CausalDAG — NetworkX-based graph engine
    graph_models.py       # Pydantic-modellen voor v2-schema (S14-02)
    validation.py         # Graph-invarianten catalog + ValidationReport (S14-04)
    graph_io.py           # JSON ↔ GEXF ↔ Markdown converters (generic)
    slider_engine.py      # Curve-functies en slider-simulatie
    prompt_builder.py     # DAG → gestructureerde LLM-prompts
    llm_connector.py      # Multi-provider LLM client
    llm_guard.py          # OWASP LLM Top 10 mitigaties (patronen uit data/llm_guard_patterns.json)
    guard_analyst.py      # Post-hoc analyse van geblokkeerde queries (CLI tool)
    license_manager.py    # Licentie-validatie en quota
    auth.py               # JWT tokens en wachtwoordhashing
  models/                 # SQLAlchemy ORM (User, License, Release)
  templates/              # Jinja2 HTML (dashboard, graph viewer, chat)
  static/                 # CSS

data/models/
  sportdeelname_graph.json  # Uitgebreid v2.3.0 model
  sportdeelname_v1.json     # Simpel model (voor referentie)

stories/                  # Kanban: backlog/, doing/, done/
tests/                    # Pytest test suite
```

## Tests

```bash
python -m pytest tests/ -v
```

De test suite dekt:

- **DAG Engine** — model laden, queries, pad-analyse, simulatie
- **Slider Engine** — curvemodellen (dampening, inverted-U, lineair)
- **Prompt Builder** — LLM-prompt templates en constraints
- **Auth** — JWT-tokens, wachtwoordhashing
- **License Manager** — tiers, quota, validatie
- **LLM Connector** — provider-configuratie, API-calls (gemockt)
- **Release Manager** — versioning, release-queries
- **API endpoints** — publieke pagina's, auth, graph, sliders
- **Integratietests** — registratie → login → verken → simuleer → AI-vraag

## Developer tooling

```bash
# Graph-validatie (cycles, orphans, duplicates, dangling refs, ...)
python scripts/validate_graph.py data/models/sportdeelname_graph.json

# Conversie tussen JSON ↔ GEXF ↔ Markdown
python scripts/convert_graph.py data/models/sportdeelname_graph.json output.gexf
python scripts/convert_graph.py data/models/sportdeelname_graph.json output.md
```

## Licentie

Zie LICENSE bestand voor details.
