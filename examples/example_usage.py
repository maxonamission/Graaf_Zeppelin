#!/usr/bin/env python3
"""Voorbeeld: een generieke graph bouwen en converteren naar GEXF / Markdown.

Example: build a generic graph and convert it to GEXF / Markdown.

Werkt op dict-niveau (geen Pydantic), zodat dezelfde converters ook voor
eenvoudige kennisgraphs buiten het sportdeelname-schema bruikbaar zijn.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running directly from the repo root.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.core.graph_io import (  # noqa: E402
    json_to_gexf,
    json_to_markdown,
    save_graph_json,
)


def main() -> None:
    print("Graaf Zeppelin — voorbeeld / example")
    print("=" * 60)

    graph = {
        "nodes": [
            {
                "id": "nederland",
                "label": "Nederland 🇳🇱",
                "properties": {"type": "land", "hoofdstad": "Amsterdam"},
            },
            {
                "id": "amsterdam",
                "label": "Amsterdam",
                "properties": {"type": "stad"},
            },
            {
                "id": "rotterdam",
                "label": "Rotterdam",
                "properties": {"type": "stad"},
            },
            {
                "id": "graaf_zeppelin",
                "label": "Graaf Zeppelin ✈️",
                "properties": {"type": "luchtschip", "actief": "1928-1937"},
            },
        ],
        "edges": [
            {
                "source": "nederland",
                "target": "amsterdam",
                "label": "heeft hoofdstad",
                "properties": {"sinds": "1814"},
            },
            {
                "source": "nederland",
                "target": "rotterdam",
                "label": "heeft stad",
            },
            {
                "source": "graaf_zeppelin",
                "target": "amsterdam",
                "label": "bezocht",
                "properties": {"jaar": "1931"},
            },
        ],
    }

    os.makedirs("output", exist_ok=True)
    json_path = "output/example_graph.json"
    gexf_path = "output/example_graph.gexf"
    md_path = "output/example_graph.md"

    save_graph_json(graph, json_path)
    print(f"  ✓ JSON   → {json_path}")

    json_to_gexf(json_path, gexf_path)
    print(f"  ✓ GEXF   → {gexf_path} (open met Gephi)")

    json_to_markdown(json_path, md_path)
    print(f"  ✓ MD     → {md_path}")

    print("=" * 60)
    print("Klaar. Bekijk de bestanden in output/.")


if __name__ == "__main__":
    main()
