#!/usr/bin/env bash
# PostToolUse hook — draait ruff op gewijzigde Python-bestanden.
#
# Leest het tool-use-event uit stdin (JSON) en pakt het file_path-veld.
# Als het een .py-bestand is, draait ruff check --fix en ruff format op
# dat bestand. Fouten gaan naar stderr maar blokkeren de hook niet — ruff
# is een hint, niet een gate in de Claude-loop.

set -uo pipefail

INPUT="$(cat)"
FILE="$(printf '%s' "$INPUT" | python3 -c 'import json, sys; d = json.load(sys.stdin); print(d.get("tool_input", {}).get("file_path", ""))' 2>/dev/null)"

if [[ -z "$FILE" || "$FILE" != *.py ]]; then
    exit 0
fi

if [[ ! -f "$FILE" ]]; then
    exit 0
fi

# Pak ruff uit de project-venv als die er is; anders PATH-ruff.
RUFF="ruff"
if [[ -x ".venv/bin/ruff" ]]; then
    RUFF=".venv/bin/ruff"
fi

"$RUFF" check --fix "$FILE" >&2 || true
"$RUFF" format "$FILE" >&2 || true
