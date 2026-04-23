# S14-06: Ontwikkelstraat parallel aan Olympus (GZ-06)

**Epic:** EPIC-14 Graph-methodologie afstemming
**Status:** 🔲 Backlog
**Prioriteit:** Gemiddeld
**Bron:** `docs/actieplan-os.md` §GZ-06

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
