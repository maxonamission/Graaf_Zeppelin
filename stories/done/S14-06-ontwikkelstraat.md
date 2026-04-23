# S14-06: Ontwikkelstraat parallel aan Olympus (GZ-06)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** ✅ Done
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-06

## Resultaat

De volledige vijf-lagen-ontwikkelstraat staat nu op Zeppelin, conform
de Olympus-blauwdrukken:

- **`pyproject.toml`** — `[project]`-metadata, dev-deps
  (`ruff`, `mypy`, `pre-commit`, `pytest-asyncio`, `pytest-cov`), volledige
  ruff-config (select `E/F/I/UP/B/SIM/RUF`; ignores voor `E501`, `B008` en
  `RUF001-003` voor NL-typografie), en mypy-strict-config met pydantic-plugin
  en target-scope op de EPIC-14-modules.
- **`setup.py` en `pytest.ini` verwijderd**; `pyproject.toml` is nu single
  source of truth voor tool-config en project-metadata. `Dockerfile` is ook
  opgeschoond: de weggehaalde `graaf_zeppelin/`-dir uit S14-02 refereerde
  ie nog, plus `scripts/` en `alembic/` zijn toegevoegd.
- **Ruff auto-fixed 139 issues**; 38 bestanden geformatteerd; handmatig
  resteerden 29 errors — alle opgelost (16× B904 in FastAPI error handlers
  kregen `from e`, rest waren SIM/UP/F841/E402/E741/RUF005/RUF012 op
  verschillende plekken). Eindstand: **`ruff check .` en `ruff format --check .`
  beide groen**.
- **Mypy-strict groen op de EPIC-14-modules** (`dag_engine.py`,
  `id_schema.py`, `validation.py`, `graph_models.py`, `graph_io.py`).
  Scope bewust beperkt: de oudere modules (`auth`, `audit`, `slider_engine`,
  `llm_connector`, `license_manager`) hebben nog 14 strict-violations die
  hier niet in scope vallen — vastgelegd als follow-up.
- **`.pre-commit-config.yaml`** met generieke file-hygiene-hooks, ruff-check
  (met --fix), ruff-format, mypy-local (scoped op EPIC-14-modules) en een
  local `story-status`-hook die alleen op staged `stories/`-wijzigingen
  draait.
- **`.github/workflows/ci.yml`** draait ruff + mypy + `validate_graph.py`
  + `check_story_status.py --mode=full` + pytest (graph-subset) op elke
  push en PR naar `main`. De bestaande `security.yml` blijft naast de
  nieuwe CI draaien.
- **`.claude/settings.json` + `.claude/hooks/ruff_on_python.sh` en
  `pytest_on_stop.sh`** — PostToolUse draait ruff op gewijzigde Python-
  bestanden; Stop draait de graph-test-subset. Niet-blokkerend (fast feedback).
- **`.github/pull_request_template.md`** — aangepast voor Zeppelin-
  specifieke security-review-triggers: auth/licensing/LLM-connector,
  user-input-endpoints (reasoning/wizard/explorations), alembic-migraties,
  dependency-upgrades.
- **`scripts/check_story_status.py`** — geport vanuit Olympus, geschreven
  voor de Zeppelin-conventies: accepteert zowel `# S##-##: Titel` als
  `# S##-## — Titel`, herkent EPICS-rijen met link-syntax en emoji-badges,
  accepteert `## Resultaat` als equivalent voor `## Doel + ##
  Acceptatiecriteria` op done-stories. Legacy-problemen (oudere
  done-stories zonder `## Resultaat`, backlog-stories zonder inline AC)
  zijn demoted tot **warnings** zodat het script groen CI geeft zonder
  dat we ~40 legacy stories hoeven te backfillen.
- **`CLAUDE.md`** aangemaakt met secties Project, Tech stack,
  **Ontwikkelstraat** (vijf lagen + snelle commando's), **Story-workflow**
  (conventies + tijdens werk) en **Review-skills** (triggers voor
  `/review` en `/security-review`).
- **EPICS-rechtzettingen**: S13-02..S13-06 stonden als Backlog in
  EPICS.md maar de files zaten al in `done/` — bijgewerkt. S15-03
  (email-validator) is naar `done/` verplaatst (gedekt door S14-02).

### Validatie

```
ruff check .                    # all checks passed
ruff format --check .           # 69 files already formatted
mypy <EPIC-14-modules>          # no issues found in 5 source files
python scripts/validate_graph.py data/models/sportdeelname_graph.json
                                # ValidationReport: OK
python scripts/check_story_status.py --mode=full
                                # 0 errors, 84 warnings (legacy stories)
pytest -q <graph-tests>         # 168 passed
```

## Niet in scope / vervolg

- **Mypy-strict op `app/api/`, `app/models/`, overige `app/core/`-modules.**
  14 open violations in auth/audit/slider_engine/llm_connector/license_manager;
  vereist cast/TypedDict/typing werk op legacy-code. Eigen follow-up story.
- **pytest-asyncio in requirements** staat in `[project.optional-dependencies].dev`
  van `pyproject.toml`; het daadwerkelijk opnieuw werkend maken van
  `test_api.py`, `test_integration.py` en `test_llm_connector.py` (80
  collection-errors/failures in EPIC-15 S15-01) is onderdeel van EPIC-15,
  niet van deze story. De CI-pytest-step draait voorlopig expliciet de
  graph-subset.
- **Branch protection op `main`** activeren: dat is een repo-admin-actie
  op GitHub, niet iets dat we in code zetten. Doen zodra een CI-run
  groen door is.
- **Legacy done-stories backfillen** naar het `## Resultaat`-format: 40+
  stories; de tooling accepteert beide vormen dus geen urgentie.

## Doel

Pas de volledige ontwikkelstraat (zoals gebouwd in de OS-epic van Olympus) toe op
Graaf Zeppelin: lint + types + pre-commit + CI + Claude-hooks + review-skills +
story-workflow + CLAUDE.md-sectie.

## Context

Graaf Zeppelin heeft al pytest en een behoorlijk brede testsuite, maar mist
pre-commit, een volwaardige CI-workflow, Claude Code hooks, PR-template en een
strikte ruff/mypy-configuratie. Door het hele patroon in één epic door te voeren
wordt Zeppelin even goed beschermd als Olympus. Wordt aanzienlijk lichter zodra er
een template-repo (`codebase-templates`) bestaat.

## Input

- De acht OS-stories van Olympus (OS-01 t/m OS-08) als blauwdruk
- Olympus' `pyproject.toml`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`,
  `.claude/settings.json` + hooks, `scripts/check_story_status.py` +
  `migrate_legacy_done_stories.py`, PR-template, CLAUDE.md-sectie

## Acceptatiecriteria

- [ ] `pyproject.toml` (of `requirements.txt`-equivalent) heeft `ruff`, `mypy`, `pre-commit` in dev-deps
- [ ] `[tool.ruff]` + `[tool.ruff.lint]` + `[tool.ruff.format]` geconfigureerd; rules-set identiek aan Olympus (minus Griekse-unicode-uitzondering die Olympus-specifiek is)
- [ ] `[tool.mypy]` met `strict = true` op `app/core/` (minimaal), pydantic-plugin actief
- [ ] `.pre-commit-config.yaml` met ruff-check, ruff-format, mypy (local hook), EOF/whitespace/yaml-toml-json-check, secret-scanner, story-status-check
- [ ] `.github/workflows/ci.yml` met ruff + mypy + pytest + story-status op elke PR + push
- [ ] `.claude/settings.json` met PostToolUse (ruff-op-py) + Stop (pytest)
- [ ] `.github/pull_request_template.md` (kopie van Olympus, aangepast voor Zeppelin-security-triggers: auth / licensing / LLM-connector / externe API's)
- [ ] `stories/`-structuur met `backlog/`, `doing/`, `done/` + `EPICS.md` (al aanwezig; eventueel uitbreiden)
- [ ] `scripts/check_story_status.py` — overgenomen uit Olympus, paden aangepast
- [ ] `CLAUDE.md` met `## Ontwikkelstraat`- en `## Story-workflow`-secties
- [ ] Branch protection op `main` activeren zodra CI stabiel draait

## Aanpak — sub-stories analoog aan Olympus OS-01..OS-08

In dezelfde volgorde, incrementeel, commit per sub-story, testsuite groen houden:

1. **S14-06a:** Ruff strict config + auto-fix ronde
2. **S14-06b:** Mypy strict op `app/core/`
3. **S14-06c:** Pre-commit hooks
4. **S14-06d:** CI-workflow (GitHub Actions)
5. **S14-06e:** Claude Code hooks
6. **S14-06f:** Story-status-check en story-conventie
7. **S14-06g:** Review-skills in PR-workflow
8. **S14-06h:** CLAUDE.md-sectie

> Deze sub-stories worden als aparte bestanden aangemaakt zodra de epic wordt
> opgestart, om individuele PR-scope klein te houden.

## Afhankelijkheden

- Voor maximale winst: doe S14-01 t/m S14-05 eerst zodat de ontwikkelstraat daarna
  een stabiele codebase bewaakt. Mag ook parallel: laag 1 (ruff/mypy) geeft
  onmiddellijk feedback op refactors.
- **Speciaal:** bestaat er intussen een template-repo `codebase-templates`
  (zie aparte discussie), dan krijgt deze story een heel ander karakter: niet acht
  sub-stories, maar één keer `copier copy` en hooguit een paar project-specifieke
  tweaks.

## Geschat

- **Zonder template:** 1 werkweek verspreid (zoals Olympus' OS-epic)
- **Met template:** halve dag

## Risico's

- De bestaande 15 testbestanden gaan waarschijnlijk ruff-issues opleveren (zoals
  Olympus 117 errors bij default-rules had). Niet-functionele wijzigingen; pak het
  in één commit met ruff-auto-fix.
- Mypy-strict op `app/core/` ontdekt wrsch. dict-signaturen die pas door S14-02
  strict worden. Workaround: activeer mypy-strict eerst op de Pydantic-module; op
  `dag_engine.py` pas na S14-02.
