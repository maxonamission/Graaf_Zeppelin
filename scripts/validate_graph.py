#!/usr/bin/env python3
"""CLI for graph validation (S14-04).

Usage:
    python scripts/validate_graph.py data/models/sportdeelname_graph.json
    python scripts/validate_graph.py data/models/sportdeelname_graph.json --json
    python scripts/validate_graph.py <path> --fail-on-warnings

Exit codes:
    0 — report is valid (no errors; warnings allowed unless --fail-on-warnings)
    1 — report has errors, or the JSON file could not be parsed
    2 — usage error (bad path, unreadable file)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as ``python scripts/validate_graph.py`` from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a graph JSON file against collection-level invariants."
    )
    parser.add_argument("path", type=Path, help="Path to the graph JSON file")
    parser.add_argument(
        "--json",
        dest="as_json",
        action="store_true",
        help="Emit the full report as JSON instead of the human summary",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Exit non-zero when warnings are present (defaults to errors only)",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2

    try:
        with args.path.open(encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"error: could not read {args.path}: {exc}", file=sys.stderr)
        return 2

    # Imported here so --help works without pulling in the DAG engine.
    from app.core.validation import validate_graph

    report = validate_graph(data)

    if args.as_json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        print(report.summary())

    if not report.is_valid:
        return 1
    if args.fail_on_warnings and report.warnings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
