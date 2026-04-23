#!/usr/bin/env python3
"""Migrate opaque node/edge IDs to the readable Vorm A schema (S14-05).

    Nodes:  N001  →  {DOMEIN-AFK}-{NIVEAU}-{VOLGNR}   e.g. UIT-L0-001
    Edges:  E001  →  E-{EDGE_TYPE_AFK}-{VOLGNR}       e.g. E-MED-014

See ``app/core/id_schema.py`` for the canonical tables and parsing
helpers. The script is idempotent: running it twice on the same file is
a no-op.

Besides rewriting ``nodes[i].id``, ``edges[i].id``, ``edges[i].source``
and ``edges[i].target``, the script also rewrites the ``related_nodes``
lists on sliders — the only other place in the v2 JSON that references
node IDs. Human-readable ``primary_clusters`` values are left untouched.

A mapping file is written to ``data/migrations/old_to_new_ids.json``
alongside the migrated data; it is the audit trail for per-node review
and for updating external references.

Usage:
    python scripts/migrate_ids.py data/models/sportdeelname_graph.json
    python scripts/migrate_ids.py <path> --dry-run
    python scripts/migrate_ids.py <path> --mapping-out other/path.json
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.core.id_schema import (
    derive_edge_id,
    derive_node_id,
    validate_edge_id,
    validate_node_id,
)


def _build_node_mapping(nodes: list[dict[str, Any]]) -> dict[str, str]:
    """Deterministic per-bucket sequence within (domain, level)."""
    counters: dict[tuple[str, str], int] = defaultdict(int)
    mapping: dict[str, str] = {}
    for node in nodes:
        old_id = node["id"]
        # Idempotence: leave already-migrated IDs alone.
        if validate_node_id(old_id):
            mapping[old_id] = old_id
            continue
        domain = node["domain"]
        level = node["level"]
        counters[(domain, level)] += 1
        mapping[old_id] = derive_node_id(domain, level, counters[(domain, level)])
    return mapping


def _build_edge_mapping(edges: list[dict[str, Any]]) -> dict[str, str]:
    """Deterministic per-bucket sequence within edge_type."""
    counters: dict[str, int] = defaultdict(int)
    mapping: dict[str, str] = {}
    for edge in edges:
        old_id = edge.get("id")
        if not old_id:
            continue  # edges without ids are rare; skip remapping
        if validate_edge_id(old_id):
            mapping[old_id] = old_id
            continue
        edge_type = edge["edge_type"]
        counters[edge_type] += 1
        mapping[old_id] = derive_edge_id(edge_type, counters[edge_type])
    return mapping


def _apply(
    data: dict[str, Any],
    node_map: dict[str, str],
    edge_map: dict[str, str],
) -> None:
    """Rewrite IDs and cross-references in place."""
    for node in data.get("nodes", []):
        node["id"] = node_map.get(node["id"], node["id"])

    for edge in data.get("edges", []):
        if edge.get("id") in edge_map:
            edge["id"] = edge_map[edge["id"]]
        # source always points to a node
        if edge.get("source") in node_map:
            edge["source"] = node_map[edge["source"]]
        # target points to a node or (for moderator edges) to an edge
        target = edge.get("target")
        if edge.get("target_type") == "edge":
            if target in edge_map:
                edge["target"] = edge_map[target]
        elif target in node_map:
            edge["target"] = node_map[target]

    for slider in data.get("sliders", []):
        related = slider.get("related_nodes")
        if isinstance(related, list):
            slider["related_nodes"] = [node_map.get(r, r) for r in related]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Migrate opaque node/edge IDs to the readable Vorm A schema."
    )
    parser.add_argument("path", type=Path, help="Graph JSON to migrate in-place")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report changes without writing the data file or the mapping",
    )
    parser.add_argument(
        "--mapping-out",
        type=Path,
        default=_REPO_ROOT / "data" / "migrations" / "old_to_new_ids.json",
        help="Where to write the audit mapping (default: data/migrations/old_to_new_ids.json)",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=3,
        help="Indent for the rewritten data file (default: 3, matches existing style)",
    )
    args = parser.parse_args(argv)

    if not args.path.exists():
        print(f"error: file not found: {args.path}", file=sys.stderr)
        return 2

    with args.path.open(encoding="utf-8") as f:
        data = json.load(f)

    node_map = _build_node_mapping(data.get("nodes", []))
    edge_map = _build_edge_mapping(data.get("edges", []))

    changed_nodes = sum(1 for old, new in node_map.items() if old != new)
    changed_edges = sum(1 for old, new in edge_map.items() if old != new)

    print(
        f"{args.path}: {changed_nodes}/{len(node_map)} node-IDs "
        f"and {changed_edges}/{len(edge_map)} edge-IDs to migrate"
    )

    if changed_nodes == 0 and changed_edges == 0:
        print("(idempotent: everything already in Vorm A — nothing to do)")
        return 0

    _apply(data, node_map, edge_map)

    if args.dry_run:
        print("(dry-run: no files written)")
        return 0

    # Write mapping BEFORE the data file, so if the data write fails we
    # still have the audit trail.
    args.mapping_out.parent.mkdir(parents=True, exist_ok=True)
    with args.mapping_out.open("w", encoding="utf-8") as f:
        json.dump(
            {"nodes": node_map, "edges": edge_map},
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        f.write("\n")
    print(f"wrote mapping → {args.mapping_out}")

    with args.path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=args.indent, ensure_ascii=False)
        f.write("\n")
    print(f"wrote data    → {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
