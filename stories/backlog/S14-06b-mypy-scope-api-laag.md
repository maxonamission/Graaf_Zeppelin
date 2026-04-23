# S14-06b: Mypy-strict uitbreiden naar FastAPI-routing-laag

**Epic:** EPIC-14 Graph-methodologie afstemming (vervolg op S14-06 + S14-06a)
**Status:** 🔲 Backlog
**Prioriteit:** Gemiddeld
**Bron:** "Niet gedaan (bewust)"-sectie van
`stories/done/S14-06a-mypy-scope-uitbreiden.md`

## Doel

Mypy-strict-scope verder uitbreiden naar `app/api/*`, `app/main.py` en
`app/db.py` — de laatste 85 violations buiten `app/core/`. Daarmee is de
hele applicatie-laag mypy-strict-groen.

## Context

S14-06a maakte de volledige `app/core/`-laag (17 bestanden) mypy-strict-
groen. Ontdekking langs de weg: `app/models/` was **al groen**. Er blijven
dus alleen FastAPI-routes (`app/api/*`), de app-entry (`app/main.py`) en
een database-helper (`app/db.py`) over.

### Verdeling (baseline van 2026-04-23, na S14-06a)

Totaal: **85 errors in 12 bestanden**.

| Bestand | Errors | Opmerking |
|---|---|---|
| `app/api/graph.py` | 19 | Grootste — alle GET/filters |
| `app/main.py` | 18 | Inclusief 1 `arg-type` op `add_exception_handler` |
| `app/api/license.py` | 8 | |
| `app/api/wizard.py` | 7 | |
| `app/api/models.py` | 6 | Inclusief 1 `assignment` (Any→CausalDAG) |
| `app/api/auth.py` | 6 | |
| `app/api/explorations.py` | 5 | |
| `app/api/deps.py` | 5 | |
| `app/api/conversations.py` | 5 | |
| `app/api/reasoning.py` | 3 | |
| `app/api/releases.py` | 2 | |
| `app/db.py` | 1 | |

### Categorieën

| Rule | Aantal | Aard |
|---|---|---|
| `no-untyped-def` | 69 | Mechanisch — return-type annotatie toevoegen aan FastAPI-routes |
| `arg-type` | 5 | Inhoudelijk — signature-mismatches |
| `type-arg` | 4 | Mechanisch — `dict` → `dict[str, Any]` |
| `no-any-return` | 4 | Mechanisch — expliciete lokale variabele of cast |
| `assignment` | 1 | Inhoudelijk (`app/api/models.py:94`, Any → CausalDAG) |
| `union-attr` | 1 | Mechanisch — None-guard toevoegen |
| `misc` | 1 | Per geval beoordelen |

## Acceptatiecriteria

- [ ] `mypy app/` groen (volledige app-laag onder strict = true)
- [ ] `.pre-commit-config.yaml` mypy-hook naar `mypy app/`
- [ ] `.github/workflows/ci.yml` mypy-step idem
- [ ] `.github/pull_request_template.md` testplan-checkbox bijgewerkt
- [ ] `CLAUDE.md §Ontwikkelstraat` bijgewerkt: scope = volledige `app/`
- [ ] 365 tests blijven groen
- [ ] Geen nieuwe `ignore_missing_imports` in overrides tenzij strikt
  nodig (bv. slowapi heeft er al één)
- [ ] Inhoudelijke errors afzonderlijk geanalyseerd — niet onder de pet
  geschoven met `# type: ignore` tenzij met toelichting waarom

## Aanpak

Per-bestand, in volgorde van grootte (kleine eerst, zodat we halverwege
een groene subset hebben):

1. **`app/db.py`** (1) — warming-up
2. **`app/api/releases.py`** (2)
3. **`app/api/reasoning.py`** (3)
4. **`app/api/deps.py`** (5) — dep-injection-signatures; let op FastAPI
   `Depends()`-pattern
5. **`app/api/conversations.py`** (5)
6. **`app/api/explorations.py`** (5)
7. **`app/api/auth.py`** (6)
8. **`app/api/models.py`** (6) — bevat inhoudelijke Any→CausalDAG
   assignment die verdient een echte analyse
9. **`app/api/wizard.py`** (7)
10. **`app/api/license.py`** (8)
11. **`app/main.py`** (18) — inclusief `add_exception_handler`
    signature-issue (mogelijk een Starlette-typing-constraint;
    anders `# type: ignore[arg-type]` met motivatie)
12. **`app/api/graph.py`** (19) — grootste, bewust als laatste zodat
    eerdere patterns zich kunnen uitkristalliseren

Daarna: config-uitbreiding (pre-commit, CI, PR-template, CLAUDE.md),
testsuite, story-close.

## Afhankelijkheden

S14-06a (vereist dat `app/core/` al groen is — beschikbaar).

## Geschat

3–4 uur. De 69 `no-untyped-def` zijn bulk maar niet triviaal — FastAPI-
routes kunnen `HTMLResponse`, `RedirectResponse`, `dict[str, Any]`,
Pydantic-models of `None` teruggeven; per route eerlijk typeren.

## Risico's

- **`add_exception_handler` in `main.py`** (arg-type) kan een Starlette-
  typing-limitatie zijn waar `# type: ignore[arg-type]` legitiem is.
- **Any→CausalDAG assignment** in `app/api/models.py:94` kan op een
  echte dict-access-zonder-guard duiden; fix kan inhoudelijk zijn en
  een kleine refactor vereisen.
- **FastAPI `Depends()`-signatures** verlangen soms subtiel andere
  type-hints dan pure Python — bv. wanneer de dep een context-manager
  is. Vraag hulp wanneer je vastloopt; niet verlokken tot het
  breken van de routering om een mypy-error te laten verdwijnen.
- **Scope-creep** — we raken 12 bestanden met routing-logica;
  verleidelijk om onderweg "kleine verbeteringen" mee te nemen die
  buiten typing vallen. Discipline: alleen typing, rest in eigen
  story.
