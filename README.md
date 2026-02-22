# Graaf Zeppelin

Causaal redeneerplatform voor sportdeelname. Combineert een wetenschappelijk onderbouwd causaal model (KNSB Sportdeelnamemodel) met een REST API en LLM-integratie, zodat sportbonden via AI-agents beleidsvragen kunnen beantwoorden.

A causal reasoning platform for sports participation. Combines a scientifically grounded causal model (KNSB Sports Participation Model) with a REST API and LLM integration, enabling sports federations to answer policy questions through AI agents.

## Features

- **Causaal model** — 69 factoren, 108 relaties, 8 beleidsinstrumenten (sliders) met wetenschappelijke onderbouwing
- **REST API** — Endpoints voor nodes, edges, domeinen, paden, sliders en simulatie
- **LLM-redenering** — Causaal gegronde antwoorden via OpenAI/Anthropic (BYOK)
- **Slider-simulatie** — Simuleer beleidsinterventies met wiskundige curvemodellen
- **Dual-schema** — Ondersteunt zowel het simpele v1-model als het uitgebreide v2.3.0-model
- **Format conversie** — JSON, GEXF en Markdown export
- **Licentiesysteem** — API-key management per organisatie

## Snelstart

```bash
git clone https://github.com/maxonamission/Graaf_Zeppelin.git
cd Graaf_Zeppelin
pip install -r requirements.txt
pip install -e .

# Start de API
uvicorn app.main:app --reload
```

De API is beschikbaar op `http://localhost:8000`. Documentatie: `http://localhost:8000/docs`.

## API Endpoints

| Endpoint | Methode | Beschrijving |
|----------|---------|-------------|
| `/api/graph/summary` | GET | Model-overzicht: domeinen, metrics, slider-count |
| `/api/graph/domains` | GET | Alle domeinen met node-counts |
| `/api/graph/factors` | GET | Alle factoren (`?domain=`, `?cluster=`, `?status=`) |
| `/api/graph/factors/{id}` | GET | Factor-detail met oorzaken, effecten, moderators |
| `/api/graph/relations` | GET | Alle relaties (`?cluster=`, `?polarity=`, `?edge_type=`) |
| `/api/graph/paths/{from}/{to}` | GET | Causale paden tussen twee factoren |
| `/api/graph/sliders` | GET | Alle beleidsinstrumenten |
| `/api/graph/sliders/{id}` | GET | Slider-detail met curve en evidence |
| `/api/graph/intervene` | POST | Simuleer impact van een factorverandering |
| `/api/graph/simulate` | POST | Simuleer slider-aanpassingen op edge-gewichten |
| `/api/reasoning/query` | POST | LLM-beantwoording met causale context (BYOK) |
| `/api/reasoning/intervene` | POST | LLM-analyse van interventie (BYOK) |

## Architectuur

```
app/
  main.py                 # FastAPI app, graph caching bij startup
  config.py               # Instellingen (model path, DB, secrets)
  api/
    graph.py              # Graph API endpoints
    reasoning.py          # LLM-redenering endpoints
    auth.py               # Authenticatie
    deps.py               # Gedeelde dependencies (auth, graph)
  core/
    dag_engine.py          # CausalDAG — NetworkX-based graph engine (v1+v2)
    slider_engine.py       # Curve-functies en slider-simulatie
    prompt_builder.py      # Gestructureerde LLM-prompts
    llm_connector.py       # Multi-provider LLM client
    license_manager.py     # Licentie-validatie en quota
  models/                  # SQLAlchemy ORM (User, License, Release)
  templates/               # Jinja2 HTML (dashboard, graph viewer)

data/models/
  sportdeelname_v1.json    # Simpel model (15 factoren, 26 relaties)
  sportdeelname_graph.json # Uitgebreid v2.3.0 model (69 nodes, 114 edges, 8 sliders)
```

## Causaal model

Het sportdeelnamemodel beschrijft factoren die sportdeelname beïnvloeden, verdeeld over 9 domeinen:

| Domein | Factoren | Voorbeeld |
|--------|----------|-----------|
| Psychologisch | 11 | Intrinsieke motivatie, Zelfeffectiviteit |
| Sociaal | 5 | Clubklimaat, Peergroep, Coach-atleet relatie |
| Training & Prestatie | 7 | Trainingsvolume, Prestatieniveau |
| Organisatie & Aanbod | 13 | IJsbaanbeschikbaarheid, Wedstrijdformat |
| Middelen & Logistiek | 8 | Financiële draagkracht, Reisafstand |
| Regels & Administratie | 8 | Licentiestatus, Categorie-indeling |
| Macro-context | 8 | Economisch klimaat, Klimaattrends |
| Discipline-specifiek | 5 | Ploegenstructuur, Seizoenscompensatie |
| Uitkomsten | 4 | Feitelijke deelname, Continuïteit |

### Sliders (beleidsinstrumenten)

8 configureerbare sliders met wiskundige curvemodellen:

- **Economisch klimaat** — Dampening threshold (recessie-effect)
- **Accommodatietoegang** — Dampening threshold (minimale ijstijd)
- **Bondsbeleid & regelgeving** — Inverted-U (optimum tussen te veel/weinig regels)
- **Prestatiecultuur** — Inverted-U (smal optimum, druk vs. uitdaging)
- **Clubklimaat & sociale cohesie** — Inverted-U (breed optimum)
- **Vrijwilligerscapaciteit** — Lineair (meer = beter)
- **Seizoen & klimaat** — Lineair (langere winter = meer participatie)
- **Levensfase & transitie** — Lineair dempend (sterkste dropout-predictor)

## CLI Tool

```bash
# JSON naar GEXF
python -m graaf_zeppelin.cli convert examples/knowledge_graph.json output.gexf

# JSON naar Markdown
python -m graaf_zeppelin.cli convert examples/knowledge_graph.json output.md
```

## Tests

```bash
python -m pytest tests/ -v
```

71 tests dekken: DAG engine (v1+v2), slider-curven, API endpoints, prompt builder, en format conversie.

## Licentie

Zie LICENSE bestand voor details.
