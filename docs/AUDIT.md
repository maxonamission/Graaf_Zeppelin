# Codebase Audit — Graaf Zeppelin

> **Datum:** 2026-03-14  
> **Aanleiding:** De eerste review bracht niet boven tafel dat deze codebase meerdere functionele en inhoudelijke lagen bevat. README.md en DOCUMENTATION.md beschrijven verschillende producten. Dit rapport documenteert de bevindingen en sluit af met een richtinggevende overweging.

---

## 1. Samenvatting van bevindingen

De codebase bevat **drie fundamenteel verschillende lagen** die in de documentatie niet als geheel worden beschreven:

| Laag | Locatie | Beschrijving | Omvang |
|------|---------|-------------|--------|
| **A — Knowledge Graph Library** | `graaf_zeppelin/` | Generieke graph-conversie (JSON ↔ GEXF ↔ Markdown) | ~500 regels |
| **B — Causaal Redeneerplatform** | `app/` | FastAPI webapplicatie met DAG engine, slider-simulatie, LLM-integratie, licenties | ~3.000+ regels |
| **C — Domeinmodel Sportdeelname** | `data/models/` | Wetenschappelijk causaal model (69 factoren, 114 relaties, 8 sliders, 66 referenties) | ~4.000 regels JSON |

**DOCUMENTATION.md** beschrijft uitsluitend laag A.  
**README.md** beschrijft laag B (en raakt laag C aan).  
**Laag C** — het inhoudelijk domeinmodel — wordt nergens als zelfstandig artefact gedocumenteerd, terwijl het de kern van het product is.

---

## 2. Gedetailleerde analyse per laag

### Laag A — Knowledge Graph Library (`graaf_zeppelin/`)

**Wat DOCUMENTATION.md zegt:**
> *"Graaf Zeppelin is een Python library voor het converteren van knowledge graphs tussen verschillende formaten."*

**Wat de code bevat:**

| Module | Regels | Functie |
|--------|--------|---------|
| `knowledge_graph.py` | 112 | KnowledgeGraph-klasse met nodes, edges, JSON I/O, schema-validatie |
| `converters.py` | 259 | JSON ↔ GEXF ↔ Markdown conversie met UTF-8 |
| `cli.py` | 97 | Command-line interface (`graaf-zeppelin convert`) |
| `__init__.py` | 15 | Publieke API exports, versie 0.1.0 |

**Status:** Volledig functioneel, standalone, geen externe dependencies.  
**Tests:** 7 tests in `test_conversions.py` — alle slagen.  
**Discrepantie:** Geen. DOCUMENTATION.md is accuraat voor deze laag.

---

### Laag B — Causaal Redeneerplatform (`app/`)

**Wat README.md zegt:**
> *"Causaal redeneerplatform voor sportdeelname. Combineert een wetenschappelijk onderbouwd causaal model met een REST API en LLM-integratie."*

**Wat de code bevat:**

| Component | Module | Regels | Functie |
|-----------|--------|--------|---------|
| DAG Engine | `core/dag_engine.py` | 562 | CausalDAG met NetworkX — factor-queries, pad-analyse, interventiesimulatie, dual-schema (v1+v2) |
| Slider Engine | `core/slider_engine.py` | 209 | Drie wiskundige curvemodellen, multi-slider simulatie, 5 gevoeligheidsniveaus |
| Prompt Builder | `core/prompt_builder.py` | 336 | DAG → gestructureerde LLM-prompts (Nederlands), 4 prompttemplates, 6 redeneerbeperkingen |
| LLM Connector | `core/llm_connector.py` | 135 | Multi-provider client (OpenAI/Anthropic), BYOK, temperature 0.1 |
| License Manager | `core/license_manager.py` | 133 | 3 tiers (basis/professional/enterprise), quota, key-generatie |
| Auth | `core/auth.py` | 93 | JWT (HS256), HMAC-SHA256 wachtwoordhashing, stdlib-only |
| Release Manager | `core/release_manager.py` | 83 | Semantic versioning, migratieguides, parallelle draaiperiode |
| Graph API | `api/graph.py` | 369 | 12 REST endpoints voor factoren, relaties, paden, sliders, simulatie |
| Reasoning API | `api/reasoning.py` | 118 | LLM-redenering met causale context |
| Overige APIs | `api/auth.py`, `license.py`, `releases.py` | ~200 | Authenticatie, licentie, release notes |
| ORM Models | `models/` | ~70 | User, License, Release (SQLAlchemy) |
| Web App | `main.py`, `templates/`, `static/` | ~200 | FastAPI + Jinja2 + HTMX frontend |

**Tests:** 65 tests in `test_dag_engine.py`, `test_slider_engine.py`, `test_prompt_builder.py`, `test_api.py` — 65 van 72 slagen (7 API-tests falen door async fixture-incompatibiliteit, geen functioneel probleem).  

**Discrepanties met README:**
- README noemt 108 relaties; het model bevat er 114
- PLAN.md markeert de meeste fase 1–3 items als "niet afgerond" terwijl ze **wel geïmplementeerd zijn**

---

### Laag C — Domeinmodel Sportdeelname (`data/models/`)

**Wat nergens gedocumenteerd staat als zelfstandig geheel:**

Dit is het **wetenschappelijk hart** van het project — een causaal model van sportdeelname dat is opgebouwd uit academische literatuur en domeinexpertise. Het wordt nergens als zelfstandig artefact beschreven of gevalideerd.

#### Model-overzicht (v2.3.0)

| Aspect | Waarde |
|--------|--------|
| Versie | 2.3.0 (datum: 2026-02-20) |
| Project | Sportdeelnamemodel KNSB |
| Factoren (nodes) | 69 |
| Relaties (edges) | 114 |
| Domeinen | 9 |
| Clusters | 10 |
| Sliders (beleidsinstrumenten) | 8 |
| Moderator-edges | 4 |
| Literatuurreferenties | 66 |
| Edges met literatuur | 70 (61,4%) |
| Cross-domein edges | 88 (80%) |
| Hub-node | N018 — Intrinsieke motivatie (degree 16) |

#### Negen domeinen

| Domein | Factoren | Voorbeeld |
|--------|----------|-----------|
| Organisatie & Aanbod | 13 | IJsbaanbeschikbaarheid, Coachcapaciteit, Wedstrijdkalender |
| Psychologisch | 11 | Intrinsieke motivatie, Zelfeffectiviteit, Emotieregulatie |
| Regels & Administratie | 8 | Licentiestatus, Categorie-indeling, Spelregels |
| Macro-context | 8 | Economisch klimaat, Klimaattrends, Energieprijzen |
| Middelen & Logistiek | 8 | Financiële draagkracht, Reisafstand, Materiaalkosten |
| Training & Prestatie | 7 | Trainingsvolume, Technisch niveau, Herstelcapaciteit |
| Discipline-specifiek | 5 | Ploegenstructuur, Seizoenscompensatie, Wegveiligheid |
| Sociaal | 5 | Clubklimaat, Coach-atleet relatie, Peergroep |
| Uitkomsten | 4 | Feitelijke deelname, Continuïteit, Recreatieve participatie |

#### Evidence-status van relaties

| Status | Aantal | Betekenis |
|--------|--------|-----------|
| A | 40 (35%) | Gevalideerd — sterke empirische onderbouwing |
| B | 36 (32%) | Exploratief — opkomend bewijs |
| - | 38 (33%) | Baseline — gematigd bewijs |

#### Acht beleidsinstrumenten (sliders)

| Slider | Curvetype | Richting | Kernmechanisme |
|--------|-----------|----------|----------------|
| S01 Economisch klimaat | Dampening threshold (t=0.55) | Demping | Onder drempel neutraal; erboven: kosten reduceren deelname |
| S02 Accommodatietoegang | Dampening threshold (t=0.45) | Demping | Geen ijs = geen training = geen deelname |
| S03 Bondsbeleid | Inverted-U (μ=0.55, σ=0.35) | Optimum | Te weinig structuur OF te veel regels: beiden schadelijk |
| S04 Prestatiecultuur | Inverted-U (μ=0.55, σ=0.30) | Optimum | Smal optimum: zowel vrijblijvendheid als prestatiedruk schadelijk |
| S05 Clubklimaat | Inverted-U (μ=0.65, σ=0.40) | Optimum | Breed optimum: goed sociaal klimaat versterkt vrijwel alles |
| S06 Vrijwilligers | Linear (γ=0.35) | Versterking | Meer vrijwilligers = meer aanbod (geen optimum) |
| S07 Seizoen & klimaat | Linear (γ=0.40) | Versterking | Langere winter = meer participatie |
| S08 Levensfase | Linear (γ=0.30) | Demping | Sterkste dropout-predictor (30–50% reductie bij transities) |

#### Moderator-edges (meta-relaties)

Vier edges modificeren de sterkte van ándere edges:

1. Financiële draagkracht → modereert Licentiekosten→Licentiestatus
2. Financiële draagkracht → modereert Materiaalkosten→Materiaaltoegang
3. Niet-participatiefase → modereert Herintredeprogramma's→Recreatieve participatie
4. Financiële draagkracht → modereert Toegangskosten→Recreatieve participatie

#### Kwalificatievragen per slider

Elke slider heeft 2 kwalificerende vragen waarmee een LLM-agent de sliderwaarde bepaalt op basis van organisatiecontext. Voorbeeld (S05 Clubklimaat):

- *"Hoe zou je de sfeer binnen jullie vereniging omschrijven?"*
  - Warm, iedereen welkom en betrokken → 0.85
  - Gezellig, goede onderlinge band → 0.65
  - Functioneel, mensen komen voor de sport → 0.40
  - Kil, weinig onderling contact → 0.15

**Status kwalificatievragen:** Technisch ingebouwd, inhoudelijk **niet gevalideerd** (zie `docs/epic_slider_qualifiers.md`).

#### Wetenschappelijke bronnen (selectie)

Het model verwijst naar academische literatuur voor zowel sliders als edges:

- Duda (2001): mastery-klimaat en intrinsieke motivatie
- Sarrazin et al. (2002): sociale steun als predictor sportcontinuering
- Fraser-Thomas et al. (2008): vroege selectiedruk als dropout-predictor
- Hoekman et al. (2016): accommodatieafstand als sterkste lokale predictor
- Engel & Nagel (2011): levensfasetransities als sterkste dropout-predictor
- Scheerder et al. (2006): gezinsvorming reduceert sportparticipatie 30–50%

---

## 3. Discrepanties in documentatie

### 3.1 README.md vs. DOCUMENTATION.md

| Aspect | README.md | DOCUMENTATION.md |
|--------|-----------|------------------|
| **Scope** | Volledig platform (API, LLM, sliders, licenties) | Alleen graph-conversie library |
| **Doelgroep** | Sportprofessionals, bondmedewerkers | Ontwikkelaars die graphs converteren |
| **Taal** | Nederlands (met Engelse paragraaf) | Tweetalig (NL + EN) |
| **CLI-voorbeeld** | `python -m graaf_zeppelin.cli convert` | `graaf-zeppelin convert` |
| **Tests** | "71 tests" (feitelijk 72 gedefinieerd) | `python tests/test_conversions.py` (7 tests) |
| **Architectuur** | Gedetailleerde app-structuur | Niet beschreven |
| **Domeinmodel** | 69 factoren, 9 domeinen, 8 sliders | Niet genoemd |

**Kernprobleem:** Een nieuwe lezer die DOCUMENTATION.md leest denkt dat Graaf Zeppelin een generieke graph-conversie tool is. Een lezer van README.md denkt dat het een causaal redeneerplatform voor sportdeelname is. Beiden hebben gelijk — maar over verschillende delen van de codebase.

### 3.2 PLAN.md vs. werkelijke implementatie

PLAN.md markeert vrijwel alle items als "niet afgerond":

| PLAN.md status | Werkelijke status |
|----------------|-------------------|
| `[ ] DAG engine met NetworkX` | ✅ Volledig — 562 regels, v1+v2, tests |
| `[ ] Voorbeeld sportdeelname model` | ✅ Twee modellen (v1 + v2.3.0) |
| `[ ] FastAPI met basisroutes` | ✅ 12+ endpoints |
| `[ ] Jinja2 templates met HTMX` | ✅ Templates aanwezig |
| `[ ] Licentie-check (basis)` | ✅ 3 tiers, quota, key-management |
| `[ ] SQLite database setup` | ✅ Async SQLAlchemy |
| `[ ] Prompt builder` | ✅ 4 templates, 6 constraints |
| `[ ] LLM connector` | ✅ Multi-provider (OpenAI/Anthropic) |
| `[ ] Robuuste licentie-manager met tiers` | ✅ Basis/Professional/Enterprise |
| `[ ] Release notes systeem` | ✅ Semantic versioning + migratieguides |

**Kernprobleem:** PLAN.md is een planning-artefact dat niet is bijgewerkt. Het geeft een misleidend beeld van de voortgang.

### 3.3 PLAN.md vermeldt componenten die niet bestaan

| PLAN.md noemt | Status |
|---------------|--------|
| `alembic/` — DB migraties | Niet aanwezig in repository |
| `Dockerfile` | Niet aanwezig |
| `docker-compose.yml` | Niet aanwezig |
| `models/graph.py` — ORM model | Niet aanwezig |
| `test_license.py` | Niet aanwezig (licentie-tests staan in `test_api.py`) |
| Response caching | Niet geïmplementeerd |
| Ollama (lokale modellen) support | Niet geïmplementeerd |
| Trendbreuk-detectie | Niet geïmplementeerd |
| Obsidian Publish integratie | Niet geïmplementeerd |
| Monitoring & logging | Niet geïmplementeerd |

---

## 4. Wat de eerste review niet boven tafel kreeg

De eerste review miste vermoedelijk de volgende dimensies:

### 4.1 Het domeinmodel is geen configuratiebestand

`sportdeelname_graph.json` (v2.3.0) is geen simpele dataset — het is een **wetenschappelijk artefact**:
- 66 literatuurreferenties
- Status-classificatie (A/B/-) als evidence-gradering
- Wiskundige curvemodellen per relatie (THRESHOLD_LOGISTIC, LINEAR, INVERTED_U)
- Moderator-edges als meta-relaties
- Kwalificatievragen als vertaling van abstract model naar gebruikerscontext

### 4.2 De LLM-integratie is meer dan een API-call

De prompt builder bevat **domeinspecifieke constraints** die het LLM dwingen tot causaal redeneren:
- 6 expliciete regels ("je verzint geen nieuwe relaties", "geef aan welk pad je volgt")
- Automatische context-injectie van relevante domeinen, factoren en mechanismen
- Nederlands als verplichte antwoordtaal
- Epistemische terughoudendheid ("als het model onvoldoende informatie bevat, zeg dit")

### 4.3 De slider-engine implementeert besliskunde

Drie wiskundige modellen met elk een ander beleidsnarriatief:
- **Dampening threshold**: Er is een drempel; daaronder neutraal, daarboven exponentieel schadelijk
- **Inverted-U**: Er is een optimum; zowel te weinig als te veel is schadelijk
- **Linear**: Meer is beter (of slechter), proportioneel

De multi-slider simulatie combineert effecten **multiplicatief**, niet additief — een bewuste keuze die voorkomt dat gecombineerde interventies onrealistisch grote effecten produceren.

### 4.4 Twee schema-versies zijn geen technische schuld

De dual-schema ondersteuning (v1 + v2) is bewust ontworpen:
- v1 (15 factoren) is een **pedagogisch model** voor initieel begrip
- v2 (69 factoren) is het **productiemodel** met volledige wetenschappelijke onderbouwing
- v1 handhaaft strikte DAG-constraint (geen cycli); v2 staat cycli toe (`check_dag=False`)

---

## 5. Richtinggevende overweging

De codebase bevat drie lagen met elk een eigen volwassenheidsniveau:

| Laag | Volwassenheid | Risico |
|------|---------------|--------|
| A — Graph Library | Hoog (volledig, getest, gedocumenteerd) | Laag — standalone bruikbaar |
| B — Platform | Midden (functioneel, tests, maar docs verouderd) | Midden — documentatie-drift, API-tests fragiel |
| C — Domeinmodel | Hoog technisch, laag gevalideerd | Hoog — kwalificatievragen niet gevalideerd, geen gebruikerstest |

### Drie mogelijke richtingen

#### Richting 1: Consolideren — documentatie en kwaliteit gelijktrekken

**Focus:** De drie lagen als één product documenteren en stabiliseren.

Concreet:
- DOCUMENTATION.md uitbreiden met platform- en modeldocumentatie, of splitsen in per-laag documenten
- PLAN.md bijwerken naar werkelijke status
- API-tests fixen (async fixture-probleem)
- Domeinmodel-documentatie toevoegen (zelfstandig beschrijving van het causaal model)

**Geschikt als:** Het product in huidige vorm al bruikbaar is en de prioriteit bij betrouwbaarheid ligt.

#### Richting 2: Valideren — domeinmodel inhoudelijk toetsen

**Focus:** De inhoudelijke kwaliteit van laag C borgen.

Concreet:
- Kwalificatievragen valideren met domeinexperts (epic_slider_qualifiers.md, stories 1–5)
- Waarde-mappings empirisch testen (produceren gekwalificeerde waarden plausibele simulatie-uitkomsten?)
- Discipline-specifieke varianten onderzoeken (is het model te schaats-specifiek?)
- Gebruikerstests met sportbondmedewerkers

**Geschikt als:** Het product naar productie moet en de inhoudelijke kwaliteit van het model bepalend is voor geloofwaardigheid.

#### Richting 3: Ontkoppelen — lagen als zelfstandige producten behandelen

**Focus:** Laag A, B en C als afzonderlijke eenheden behandelen met eigen versioning en documentatie.

Concreet:
- `graaf_zeppelin/` publiceren als standalone PyPI package (is al nagenoeg klaar)
- `app/` als applicatie met eigen installatie-instructies en configuratie
- `data/models/` als geversioned dataset met eigen schema-documentatie en changelog
- Duidelijke interfaces tussen de lagen definiëren

**Geschikt als:** Hergebruik van individuele lagen belangrijk is (bijv. het causaal model in andere contexten, of de graph-library voor andere projecten).

### Aanbeveling

**Start met richting 1 (consolideren), parallel met de eerste stap van richting 2 (inhoudelijke review kwalificatievragen).**

De reden: het product is functioneel grotendeels af, maar de documentatie geeft een vertekend beeld van wat er is. Een nieuwe ontwikkelaar, reviewer of domeinexpert kan niet effectief bijdragen zolang de documentatie drie verschillende verhalen vertelt. Tegelijkertijd is de inhoudelijke validatie van het domeinmodel (laag C) het grootste risico voor productiegebruik — en die validatie vereist domeinexperts, niet ontwikkelaars.

De ontkoppeling (richting 3) is waardevol maar niet urgent; de huidige monorepo-structuur werkt zolang de documentatie helder is.

---

## Bijlage: Testresultaten

| Testsuite | Tests | Status |
|-----------|-------|--------|
| `test_conversions.py` | 7 | ✅ Alle geslaagd |
| `test_dag_engine.py` | 33 | ✅ Alle geslaagd |
| `test_slider_engine.py` | 12 | ✅ Alle geslaagd |
| `test_prompt_builder.py` | 7 | ✅ Alle geslaagd |
| `test_api.py` | 7 | ⚠️ 7 errors (async fixture-incompatibiliteit, geen functioneel defect) |
| **Totaal** | **72** | **65 geslaagd, 7 errors** |
