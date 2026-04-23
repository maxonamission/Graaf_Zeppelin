# S15-01: async testing-plugin + fixtures herstellen

**Epic:** EPIC-15 Testsuite-rehabilitatie
**Status:** 🔲 Backlog
**Prioriteit:** HOOG
**Bron:** Gevonden tijdens S14-01-validatie (2026-04-23)

## Probleem

De testsuite heeft **één kernoorzaak** die ~80 test-errors en -failures
verklaart over 8 testbestanden:

> **`pytest-asyncio` is niet geïnstalleerd.**

`pytest.ini` staat al op `asyncio_mode = auto`, maar bij het draaien meldt
pytest `PytestConfigWarning: Unknown config option: asyncio_mode` — de
plugin die die optie zou moeten lezen is er niet. Gevolg:

- Elke `@pytest.mark.asyncio` → `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`
- Elke async-fixture waar een (schijnbaar sync) test op leunt →
  `PytestRemovedIn9Warning: ... requested an async fixture 'setup_db' with
  autouse=True, with no plugin or hook that handled it. This is usually an
  error, ... This will turn into an error in pytest 9.` (nu al: **collection
  error**)
- Elke `async def test_...` →
  `Failed: async def functions are not natively supported. You need to
  install a suitable plugin` (nu al: **test failure**)

`requirements.txt` bevat **geen** `pytest-asyncio`, wat verklaart waarom de
CI-omgeving of een verse venv dit structureel mist.

## Getroffen test-bestanden (indicatief, na `pip install pydantic[email]` en
`SECRET_KEY` gezet)

| Bestand | Aard |
|---|---|
| `tests/test_api.py` | 22 collection-errors (elke test leunt op `setup_db` autouse async fixture) |
| `tests/test_authorization.py` | 9 collection-errors (idem) |
| `tests/test_integration.py` | 10 collection-errors (idem) |
| `tests/test_new_features.py` | 17 collection-errors (idem) |
| `tests/test_license_manager.py` | 13 fixture-errors op individuele async-fixture-tests |
| `tests/test_release_manager.py` | 10 idem |
| `tests/test_llm_connector.py` | 7 failures: "async def functions are not natively supported" |

Dit is pre-existing; S14-01 raakt alleen `app/core/dag_engine.py` en
`tests/test_dag_engine.py` (78 graph-tests blijven groen).

## Doel

Async-testing weer werkend in lokale venv **en** CI, zonder workaround in
individuele tests. Eén duidelijke plugin-keuze (`pytest-asyncio`), één mode
(`auto` — zoals nu al in `pytest.ini`).

## Acceptatiecriteria

- [ ] `requirements.txt` (of een dev-deps-sectie) bevat `pytest-asyncio` met
  een concrete versie-pin die de versie in `pytest.ini` (`asyncio_mode=auto`)
  ondersteunt (minimaal `>=0.23`)
- [ ] Lokale run van `pytest tests/` met alleen de vereiste env-vars (`SECRET_KEY`,
  `DATABASE_URL`) geeft **0 collection-errors** en **0 "async not supported"-
  failures**
- [ ] Eventuele resterende failures na deze story zijn **inhoudelijk** (test-logica),
  niet infra; volgen in S15-02
- [ ] CI (GitHub Actions workflow) installeert de dep en draait schoon; voeg
  `pytest-asyncio` ook toe aan een eventueel bestaand CI-deps-install-commando
- [ ] Warnings over `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio` verdwijnen
- [ ] Warnings over `PytestConfigWarning: Unknown config option: asyncio_mode` verdwijnen

## Aanpak

1. `pip install 'pytest-asyncio>=0.23'` lokaal; valideer dat `pytest.ini`-
   regel `asyncio_mode = auto` niet meer als onbekend wordt geflagd
2. Draai volledige suite; noteer welke failures overblijven (dat zijn er duidelijk
   minder; ze zijn onderwerp van S15-02)
3. Voeg dep toe aan `requirements.txt` of scheid dev-deps (bv. via een
   `requirements-dev.txt`, passend bij bestaande conventies van de repo)
4. Check `.github/workflows/`; breid installatie uit als nodig
5. Draai CI, verifieer groen

## Afhankelijkheden

Geen. Staat los van EPIC-14.

## Geschat

30 minuten tot 1 uur (dep toevoegen, CI-verifiëren).

## Risico's

- `pytest-asyncio` kan bij versie-mismatch conflicteren met `anyio` (al
  geïnstalleerd). Mitigatie: pin conservatief op een recente versie die
  beide ondersteunt.
- Nadat async-infra werkt, kunnen er alsnog individuele async-tests falen op
  inhoud (bv. async DB-setup die elders een race-condition heeft). Die
  horen bij **S15-02**, niet hier.
