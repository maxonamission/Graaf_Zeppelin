# S15-03: `email-validator` ontbreekt als expliciete dependency

**Epic:** EPIC-15 Testsuite-rehabilitatie
**Status:** 🔲 Backlog
**Prioriteit:** LAAG
**Bron:** Gevonden tijdens S14-01-validatie (2026-04-23)

## Probleem

Tijdens test-collection stuiten `tests/test_integration.py`,
`tests/test_authorization.py` en `tests/test_sprint4.py` op:

```
ImportError: email-validator is not installed,
run `pip install 'pydantic[email]'`
```

Ergens in het importpad staat een Pydantic-model met `EmailStr`, waarvoor
het `email-validator`-pakket vereist is. Dit pakket is **geen transitieve
dep** van `pydantic` zelf — je moet expliciet `pydantic[email]` installeren
of `email-validator` als losse regel in `requirements.txt` zetten. In de
huidige `requirements.txt` ontbreekt beide.

## Waarom een aparte story

Dit is een vijf-minuten-fix, maar de reden dat het apart staat:

1. De fout treedt vóór de S15-01-async-plugin-fix op (bij import-tijd). Na
   S15-01 is dit een van de weinig overblijvende collection-blockers.
2. **Scope-overlap met S14-02** (Pydantic-modellen): S14-02 voegt als
   acceptatiecriterium al `pydantic[email]>=2.6` toe aan `requirements.txt`.
   Áls S14-02 eerder wordt opgepakt dan S15-03, is deze story **klaar door
   meelifting** — markeer dan als "Done (gedekt door S14-02)".
3. Blijft nuttig als losse story voor het geval iemand eerst de testsuite
   wil opschonen zonder op S14-02 te wachten.

## Doel

De testsuite kan compleet worden gecollecteerd in een verse venv met alleen
`pip install -r requirements.txt`, zonder handmatige aanvulling.

## Acceptatiecriteria

- [ ] `requirements.txt` bevat `pydantic[email]>=2.6` **of** een aparte
      `email-validator` regel, conform conventie in de repo
- [ ] In een schone venv faalt `pytest --collect-only` niet langer op
      `ImportError: email-validator is not installed`
- [ ] Indien S14-02 tussentijds is gelanded: close deze story met een
      referentie naar de S14-02-commit (geen duplicate-werk)

## Aanpak

Eén regel in `requirements.txt` toevoegen; `pip install -r requirements.txt`
draaien; testsuite collecteren.

## Afhankelijkheden

Geen. Kan parallel met S15-01 of solo.

## Geschat

5 minuten.

## Risico's

Geen.
