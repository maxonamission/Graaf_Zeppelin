#!/usr/bin/env python3
"""Convert a graph between JSON, GEXF and Markdown formats.

Usage:
    python scripts/convert_graph.py input.json output.gexf
    python scripts/convert_graph.py input.json output.md
    python scripts/convert_graph.py input.gexf output.json
    python scripts/convert_graph.py input.md output.json

Replaces the retired ``python -m graaf_zeppelin.cli convert ...`` as part
of S14-02's consolidation.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert a graph between JSON, GEXF and Markdown formats."
    )
    parser.add_argument("input", type=Path, help="Input file (.json, .gexf, .md)")
    parser.add_argument("output", type=Path, help="Output file (.json, .gexf, .md)")
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 2

    # Imported here so --help works without loading the full module.
    from app.core.graph_io import (
        gexf_to_json,
        json_to_gexf,
        json_to_markdown,
        markdown_to_json,
    )

    src, dst = args.input.suffix.lower(), args.output.suffix.lower()
    routes: dict[tuple[str, str], callable] = {  # type: ignore[type-arg]
        (".json", ".gexf"): json_to_gexf,
        (".gexf", ".json"): gexf_to_json,
        (".json", ".md"): json_to_markdown,
        (".md", ".json"): markdown_to_json,
    }

    fn = routes.get((src, dst))
    if fn is None:
        print(
            f"error: unsupported conversion {src} → {dst}. Supported: "
            ".json↔.gexf, .json↔.md",
            file=sys.stderr,
        )
        return 2

    fn(args.input, args.output)
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
