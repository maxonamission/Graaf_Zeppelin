<!--
PR-template voor Graaf Zeppelin (S14-06). Vul elk blok in.
Zie CLAUDE.md § "Review-skills" voor wanneer welke skill draaien.
-->

## Samenvatting

<!-- Wat verandert deze PR, en waarom? Maximaal 3 bullets. -->

-
-
-

## Testplan

<!-- Hoe is deze wijziging geverifieerd? -->

- [ ] `ruff check .` en `ruff format --check .` groen
- [ ] `mypy app/core/dag_engine.py app/core/id_schema.py app/core/validation.py app/core/graph_models.py app/core/graph_io.py` groen
- [ ] `pytest -q tests/test_dag_engine.py tests/test_id_schema.py tests/test_validation.py tests/test_graph_models.py tests/test_conversions.py tests/test_slider_engine.py tests/test_prompt_builder.py` groen
- [ ] `python scripts/validate_graph.py data/models/sportdeelname_graph.json` geeft `is_valid=True`
- [ ] `python scripts/check_story_status.py --mode=full` groen
- [ ] Aanvullend handmatig getest (indien relevant):

## Geraakte stories

<!--
Welke stories raakt deze PR? Volg de S14-06-conventie: verplaats
tussen backlog/doing/done en werk EPICS.md bij. Lijst ze hieronder.
-->

- [ ] `stories/done/S##-##.md` (was `doing` / `backlog`) — AC afgevinkt of Resultaat-blok ingevuld; status in EPICS.md bijgewerkt

## Review

<!-- Laag 5 van de ontwikkelstraat. Zie CLAUDE.md voor de triggers. -->

- [ ] `/review` gedraaid; commentaar verwerkt of expliciet besproken
- [ ] `/security-review` gedraaid — **verplicht** bij wijzigingen in:
  - `app/core/auth.py`, `app/api/auth.py` of token-/sessiebeheer
  - `app/core/license_manager.py`, `app/api/license.py` of licentie-/quota-logica
  - `app/core/llm_connector.py`, `app/core/llm_guard.py` of LLM-prompt-paden
  - endpoints die user-input accepteren (reasoning, wizard, explorations)
  - database-migraties onder `alembic/`
  - dependency-upgrades in `requirements.txt` of `pyproject.toml`

## Notities voor de reviewer

<!-- Optioneel. Context die niet uit de diff blijkt: afwegingen,
     alternatieven die je hebt overwogen, bekende beperkingen. -->
