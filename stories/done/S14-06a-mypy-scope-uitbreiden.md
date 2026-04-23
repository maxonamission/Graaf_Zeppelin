# S14-06a: Mypy-scope uitbreiden naar de oudere `app/core/`-modules

**Epic:** EPIC-14 Graph-methodologie afstemming (follow-up op S14-06)
**Status:** ✅ Done
**Prioriteit:** Gemiddeld
**Bron:** "Niet in scope / vervolg"-sectie van `stories/done/S14-06-ontwikkelstraat.md`

## Resultaat

Alle 14 openstaande mypy-strict-violations in de 5 oudere `app/core/`-
modules opgelost. **Volledige `app/core/`-laag (17 bestanden) is nu
mypy-strict-groen.** Alle 365 tests blijven groen.

Per module:

- **`app/core/auth.py`** (3 errors) — `dict` → `dict[str, Any]` op
  `create_access_token` en de return-annotatie van
  `decode_access_token`; plus een `isinstance(payload, dict)`-guard na
  `json.loads` zodat het return-type klopt. `from typing import Any`
  toegevoegd.
- **`app/core/license_manager.py`** (2 errors) — `dict` →
  `dict[str, Any]` op `get_license_info` en `get_daily_usage`.
  `typing.Any` toegevoegd.
- **`app/core/llm_connector.py`** (2 errors) — de return-waardes van
  `_call_openai` en `_call_anthropic` via expliciet getypeerde lokale
  variabele (`content: str = ...`) opgelost; voorkomt de
  `no-any-return` zonder de JSON-parse te runtime-typen.
- **`app/core/audit.py`** (1 error) — `entry: dict[str, Any]`
  annotatie toegevoegd zodat toevoegen van `entry["extra"] = extra`
  (een dict) niet langer conflicteert met het initial-waarden-
  geïnferde `dict[str, int | str | None]`.
- **`app/core/slider_engine.py`** (6 errors) — `_CURVE_FUNCTIONS` kreeg
  een expliciet type `dict[str, Callable[..., float]]`. Ellipsis in de
  Callable dekt de verschillende parameter-signaturen per curve
  (t/b, mu/sigma, gamma). `collections.abc.Callable` import toegevoegd.

Config-uitbreiding:

- **`pyproject.toml`** — geen wijziging nodig; de globale
  `[tool.mypy]`-config is al `strict = true`, scope wordt bepaald door
  het CLI-argument.
- **`.pre-commit-config.yaml`** — mypy-hook van hand-picked module-
  lijst naar `mypy app/core/`.
- **`.github/workflows/ci.yml`** — idem.
- **`.github/pull_request_template.md`** — testplan-checkbox
  bijgewerkt.
- **`CLAUDE.md §Ontwikkelstraat`** — documentatie weerspiegelt de
  bredere scope; de oudere-modules-exclusie is verwijderd.

### Acceptatiecriteria

- [x] `mypy app/core/` groen op `strict = true` (14 → 0 violations)
- [x] `pyproject.toml` mypy-config ongewijzigd (alleen CLI-target
  veranderde)
- [x] `.pre-commit-config.yaml` mypy-hook scope: `app/core/`
- [x] `.github/workflows/ci.yml` mypy-step idem
- [x] `CLAUDE.md §Ontwikkelstraat` bijgewerkt
- [x] Alle 365 tests blijven groen
- [x] Resultaat-blok beschrijft per module welke typing-tweaks zijn
  toegepast

## Niet gedaan (bewust)

**`app/api/`, `app/main.py`, `app/models/`** (samen ~85 violations)
blijven buiten scope. Dat is grotendeels:

- FastAPI-route-handlers zonder expliciete return-types (47+)
- SQLAlchemy `Mapped[]`-types die mypy-strict-onvriendelijk zijn
  wanneer `dict` → Mapped-conversions uitpakken tot `Any`
- Enkele inhoudelijke fouten (`app/api/models.py:94` Any→CausalDAG
  assignment, `app/main.py:52` add_exception_handler-signatuur)

Een eigen follow-up-story kan die aanpakken indien gewenst; deze
splitsing matcht wat S14-06 al voorzag.

## Doel

De 14 mypy-strict-violations in de oudere `app/core/`-modules (auth,
audit, slider_engine, llm_connector, license_manager) oplossen en de
mypy-scope in pre-commit en CI uitbreiden zodat deze modules niet
langer als uitzondering behandeld worden.

## Context

S14-06 introduceerde mypy-strict maar beperkte de scope bewust tot de
EPIC-14-modules (`dag_engine.py`, `id_schema.py`, `validation.py`,
`graph_models.py`, `graph_io.py`) omdat de oudere modules 14
violations hadden die buiten scope van die story vielen. Deze story
pakt precies die 14 op.

Een bredere uitbreiding naar `app/api/*`, `app/main.py` en
`app/models/*` (nog eens ~85 errors) valt buiten deze story en vereist
een eigen afweging; FastAPI-routing en SQLAlchemy-`Mapped[]` geven
meer inhoudelijke typing-overwegingen dan de `app/core/`-laag.

## Acceptatiecriteria

- [ ] `mypy app/core/` groen op `strict = true` (alle 14 violations
  opgelost, geen nieuwe)
- [ ] `pyproject.toml` mypy-override-list blijft ongewijzigd of wordt
  zo smal mogelijk — we willen geen nieuwe `ignore_missing_imports`
  tenzij nodig
- [ ] `.pre-commit-config.yaml` mypy-hook krijgt `app/core/` als scope
  i.p.v. de huidige hand-picked modules
- [ ] `.github/workflows/ci.yml` mypy-step idem
- [ ] `CLAUDE.md §Ontwikkelstraat` bijwerken: "strict-scope: `app/core/`"
- [ ] Alle 365 tests blijven groen
- [ ] Resultaat-blok beschrijft per module welke typing-tweaks zijn
  toegepast (cast, explicit annotation, dict[str, Any], etc.)

## Aanpak

Per bestand, errors fixen en meteen lokaal mypy re-runnen:
1. `auth.py` — 3 errors (2× type-arg, 1× no-any-return)
2. `license_manager.py` — 2 errors (2× type-arg)
3. `llm_connector.py` — 2 errors (2× no-any-return)
4. `audit.py` — 1 error (assignment, vereist korte designcheck)
5. `slider_engine.py` — 6 errors (3× no-any-return + 3× operator
   op een dict-of-callables; vereist `Callable`-annotatie)

Daarna config-uitbreiding en test-run.

## Afhankelijkheden

Geen; S14-06 is al live.

## Geschat

1–1.5 uur.

## Risico's

- `slider_engine.py`'s callable-dict is de enige waar typing niet-
  triviaal is; als de natuurlijke `Callable[..., float]`-signatuur
  niet matcht met de échte functies dan moet het type breder, of
  moeten de functies zelf netter getypeerd.
- `audit.py`'s assignment-error kan duiden op een echte bug (dict
  toewijzen aan een veld dat `int | str | None` verwacht); correcte
  fix kan inhoudelijk zijn i.p.v. puur typing.
