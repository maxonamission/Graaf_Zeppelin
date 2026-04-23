#!/usr/bin/env bash
# Stop hook — draait de graph-subset van pytest als snelle sanity check
# aan het eind van een Claude-sessie. Rapporteert faalresultaat naar
# stderr; blokkeert de Stop niet.

set -uo pipefail

PYTHON="python3"
if [[ -x ".venv/bin/python" ]]; then
    PYTHON=".venv/bin/python"
fi

TESTS=(
    tests/test_dag_engine.py
    tests/test_id_schema.py
    tests/test_validation.py
    tests/test_graph_models.py
    tests/test_conversions.py
    tests/test_slider_engine.py
    tests/test_prompt_builder.py
)

"$PYTHON" -m pytest -q "${TESTS[@]}" >&2 || true
