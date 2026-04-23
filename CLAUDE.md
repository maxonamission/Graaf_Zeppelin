# CLAUDE.md — Graaf Zeppelin

## Project

Graaf Zeppelin is een beleidsverkenner voor sportdeelname: een webapp die
een causaal model (v2-schema, 69 knopen, 108 edges over 9 domeinen) laadt
en via een LLM natuurlijke-taal-vragen beantwoordt en interventies
doorrekent. Doelgroep: beleidsmedewerkers van sportbonden, gemeenten en
clubs zonder technische achtergrond.

Lees voor meer context:
- `README.md` — installatie, architectuur, kernprincipes
- `PLAN.md` — fasering en openstaand werk
- `docs/actieplan-os.md` — cross-project actieplan vanuit Codebase-Olympus
  (basis van EPIC-14)
- `docs/id-schema.md` — ID-conventies voor nodes en edges (S14-05)
- `docs/uniforme-kenmerken-taxonomie.md` — cross-project wens voor
  uniforme graph-object-taxonomie

## Tech stack en constraints

- **Python 3.11** (geen 3.13)
- **FastAPI** backend, **Jinja2 + HTMX + D3** frontend, **SQLAlchemy
  + aiosqlite/asyncpg** voor persistence, **Alembic** voor migraties
- **NetworkX** voor de graph-laag; **Pydantic v2** als schema-poort
  boven het v2-JSON (`app/core/graph_models.py`, S14-02)
- Encoding: UTF-8, geen BOM
- Documentatie in **Nederlands**; code-identifiers/docstrings in
  **Engels** bij uitzondering, in NL als het domein-inhoudelijk is
  (bv. model-velden als `bond_influence`, `slider_sensitivity`)

## Ontwikkelstraat

Vijf lagen van bescherming, van lokaal naar remote:

1. **Ruff** (`pyproject.toml` → `[tool.ruff]`) — lint + format. Regels:
   `E/F/I/UP/B/SIM/RUF`. Ignore: `E501, B008, RUF001-003` (zie toelichting
   in pyproject). Tests/scripts hebben een kleine extra-ignore-set.
2. **Mypy strict** — geconfigureerd in `pyproject.toml`. Scope omvat
   de **volledige `app/core/`-laag** (na S14-06a):
   ```
   mypy app/core/
   ```
   `app/api/`, `app/main.py` en `app/models/` blijven buiten scope
   (~85 FastAPI-routing- en SQLAlchemy-`Mapped[]`-violations die
   afzonderlijke typing-aandacht vereisen).
3. **Pre-commit** (`.pre-commit-config.yaml`) — draait ruff-check,
   ruff-format, mypy (op scope), file-hygiene-hooks, secret-scanner
   en `scripts/check_story_status.py --mode=staged`. Installeer met:
   ```
   pip install -e ".[dev]" && pre-commit install
   ```
4. **CI** (`.github/workflows/ci.yml`) — zelfde checks op een schone
   runner + `scripts/validate_graph.py` op het ingechecte model +
   `check_story_status.py --mode=full` + pytest op de graph-tests.
   Niet te omzeilen met `--no-verify`.
5. **Claude Code hooks** (`.claude/settings.json`) — PostToolUse draait
   ruff op gewijzigde Python-bestanden; Stop draait de graph-tests. Niet
   blokkerend; bedoeld als fast feedback tijdens het werken.

### Snelle lokale commando's

```bash
# Alles in één keer (wat pre-commit ook doet)
ruff check .                # lint
ruff format --check .       # formattering check
mypy app/core/

# Graph-gezondheid
python scripts/validate_graph.py data/models/sportdeelname_graph.json

# Story-hygiëne
python scripts/check_story_status.py --mode=full

# Tests (subset; hele suite vereist S15-01 pytest-asyncio)
pytest -q tests/test_dag_engine.py tests/test_id_schema.py \
          tests/test_validation.py tests/test_graph_models.py \
          tests/test_conversions.py tests/test_slider_engine.py \
          tests/test_prompt_builder.py
```

## Story-workflow

Stories leven onder `stories/` in drie mappen: `backlog/`, `doing/`,
`done/`. Overzicht en status in `stories/EPICS.md`. Checker:
`scripts/check_story_status.py`.

**Conventies:**

- Eén bestand per story met patroon `S##-##-korte-naam.md`. Eerste regel
  is ofwel `# S14-01: Cycle-check per edge-type` (nieuwer) of
  `# S11-01 — Authenticatie hardening` (ouder); beide worden
  geaccepteerd.
- Backlog/doing-stories hebben een `## Doel` én `## Acceptatiecriteria`-
  sectie met checkboxes. Done-stories mogen die vervangen door een
  `## Resultaat`-sectie.
- Status-locatie en status-badge in `EPICS.md` moeten overeenkomen.
- Bij het voltooien van een story: verplaats het bestand naar `done/`
  (met `git mv`), werk `EPICS.md` bij, vul een `## Resultaat`-blok in.

**Tijdens werk:**

- Pak een story door hem naar `doing/` te verplaatsen en de status in
  EPICS.md naar `🚧 Doing` te zetten.
- Eén story tegelijk. Splits grote stories op in sub-stories
  (bv. S14-06a, S14-06b, ...) als de scope boven een halve dag werk komt.

## Review-skills

Twee skill-aanroepen die we vanuit de PR-flow triggeren:

- **`/review`** — algemene code-review. Draai op elke PR vóór request.
- **`/security-review`** — **verplicht** bij wijzigingen aan:
  - `app/core/auth.py`, `app/api/auth.py` of token-/sessiebeheer
  - `app/core/license_manager.py`, `app/api/license.py` of licentie-/
    quota-logica
  - `app/core/llm_connector.py`, `app/core/llm_guard.py` of
    LLM-prompt-paden
  - endpoints die user-input accepteren (reasoning, wizard, explorations)
  - database-migraties onder `alembic/`
  - dependency-upgrades in `requirements.txt` of `pyproject.toml`

De PR-template (`.github/pull_request_template.md`) heeft checklist-
items voor beide. Laat ze expliciet staan; afvinken pas als de skill
gedraaid en commentaar verwerkt is.

## Werkwijze

- Schrijf geen code voordat de structuur besproken is; begin met een
  plan in structured prose.
- Wees expliciet over wat je hebt gelezen vs. wat je aanneemt. Vlag
  onzekerheden.
- Gebruik type hints overal. Pydantic-models voor data-validatie.
- Git commits: conventionele commits (feat/fix/docs/refactor/...); body
  in het Nederlands; referentie naar story-ID waar van toepassing.
- Commits klein en rangschikbaar per sub-story; CI moet groen zijn vóór
  merge naar `main`.

## Niet-scope (bewust)

- **Monorepo met Olympus.** We delen methodologie (via
  `docs/actieplan-os.md`, `docs/uniforme-kenmerken-taxonomie.md`), niet
  een codebase.
- **Volledige mypy-strict op alle modules.** Auth/audit/slider_engine/
  llm_connector/license_manager blijven buiten scope totdat er een
  aparte story voor is.
- **Schaalvergroting voorbereiden** (10⁵+ knopen). Niet relevant voor
  de huidige 69-nodes-dataset.
- **Frontend-refactor.** Jinja2 + HTMX + D3 is bewust gekozen voor de
  doelgroep; geen React-migratie.
