#!/usr/bin/env python3
"""Remove the ``time_lag`` field from every edge in a graph JSON file (S14-03).

Pad B, per ``docs/actieplan-os.md``: the field lives in the schema but is
never read by the simulation, so it was a dead-field anti-pattern. Pad A
(activating ``time_lag`` in an iterative-tick simulation) is parked as a
future epic (see ``PLAN.md`` under Fase 4).

The script is idempotent: running it twice is a no-op on an already-
migrated file. Writes back in place; use version control or ``--dry-run``
to inspect the diff beforehand.

Usage:
    python scripts/strip_time_lag.py data/models/sportdeelname_graph.json
    python scripts/strip_time_lag.py <path> --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Remove `time_lag` from every edge in a graph JSON file."
    )
    parser.add_argument("path", type=Path, help="Path to the graph JSON file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report what would be removed without writing the file",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=3,
        help="Indent width when writing back (default: 3, matches existing file style)",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2

    with args.path.open(encoding="utf-8") as f:
        data = json.load(f)

    edges = data.get("edges", [])
    removed = 0
    for edge in edges:
        if "time_lag" in edge:
            del edge["time_lag"]
            removed += 1

    print(f"{args.path}: removed `time_lag` from {removed}/{len(edges)} edge(s)")

    if args.dry_run:
        print("(dry-run: no file written)")
        return 0

    if removed == 0:
        print("(idempotent: file already clean, nothing written)")
        return 0

    with args.path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=args.indent, ensure_ascii=False)
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
