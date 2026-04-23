"""Graph-format conversions (JSON ↔ GEXF ↔ Markdown) — S14-02.

Moved here from the retired ``graaf_zeppelin/converters.py`` as part of
consolidating into a single canonical graph-handling package.

These converters are intentionally **generic** and work on raw dicts
with ``{"nodes": [...], "edges": [...]}`` shape. They do NOT depend on
the strict v2 Pydantic model in ``graph_models.py`` — format conversion
shouldn't require the semantic schema. The ``Graph`` model and these
converters therefore coexist as two complementary tools on the same
dict representation.

All file I/O uses UTF-8.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

PathLike = str | Path


# ── JSON I/O ─────────────────────────────────────────────────────────


def load_graph_json(path: PathLike) -> dict[str, Any]:
    """Load a graph JSON file. Returns a dict with ``nodes`` and ``edges`` lists."""
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    return _normalize_shape(data)


def save_graph_json(data: dict[str, Any], path: PathLike, indent: int = 2) -> None:
    """Save a graph dict to JSON (UTF-8, non-ASCII preserved)."""
    with Path(path).open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def _normalize_shape(data: Any) -> dict[str, Any]:
    """Ensure ``data`` is a dict with list-valued ``nodes`` and ``edges``."""
    if not isinstance(data, dict):
        raise ValueError(f"Expected a dict at the top level, got {type(data).__name__}")
    data.setdefault("nodes", [])
    data.setdefault("edges", [])
    if not isinstance(data["nodes"], list):
        raise ValueError("'nodes' must be a list")
    if not isinstance(data["edges"], list):
        raise ValueError("'edges' must be a list")
    return data


# ── JSON ↔ GEXF ──────────────────────────────────────────────────────


def json_to_gexf(json_path: PathLike, gexf_path: PathLike) -> None:
    """Convert a JSON graph to GEXF (Gephi Exchange Format)."""
    data = load_graph_json(json_path)

    gexf = ET.Element(
        "gexf",
        {"xmlns": "http://www.gexf.net/1.2draft", "version": "1.2"},
    )
    graph = ET.SubElement(
        gexf,
        "graph",
        {"mode": "static", "defaultedgetype": "directed"},
    )

    nodes_elem = ET.SubElement(graph, "nodes")
    for node in data["nodes"]:
        attrs = {
            "id": str(node.get("id", "")),
            "label": str(node.get("label", node.get("id", ""))),
        }
        node_elem = ET.SubElement(nodes_elem, "node", attrs)
        _write_attvalues(node_elem, node)

    edges_elem = ET.SubElement(graph, "edges")
    for idx, edge in enumerate(data["edges"]):
        attrs = {
            "id": str(edge.get("id", idx)),
            "source": str(edge.get("source", "")),
            "target": str(edge.get("target", "")),
        }
        label = edge.get("label") or edge.get("mechanism")
        if label:
            attrs["label"] = str(label)
        edge_elem = ET.SubElement(edges_elem, "edge", attrs)
        _write_attvalues(edge_elem, edge)

    tree = ET.ElementTree(gexf)
    ET.indent(tree, space="  ")
    tree.write(str(gexf_path), encoding="utf-8", xml_declaration=True)


def gexf_to_json(gexf_path: PathLike, json_path: PathLike) -> None:
    """Convert a GEXF graph back to our JSON shape."""
    tree = ET.parse(str(gexf_path))
    root = tree.getroot()
    ns = {"gexf": "http://www.gexf.net/1.2draft"}

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    nodes_elem = root.find(".//gexf:nodes", ns) or root.find(".//nodes")
    if nodes_elem is not None:
        iter_nodes = nodes_elem.findall(".//gexf:node", ns) or nodes_elem.findall(".//node")
        for node in iter_nodes:
            entry: dict[str, Any] = {
                "id": node.get("id"),
                "label": node.get("label", node.get("id")),
            }
            props = _read_attvalues(node, ns)
            if props:
                entry["properties"] = props
            nodes.append(entry)

    edges_elem = root.find(".//gexf:edges", ns) or root.find(".//edges")
    if edges_elem is not None:
        iter_edges = edges_elem.findall(".//gexf:edge", ns) or edges_elem.findall(".//edge")
        for edge in iter_edges:
            entry = {
                "source": edge.get("source"),
                "target": edge.get("target"),
            }
            if edge.get("label"):
                entry["label"] = edge.get("label")
            props = _read_attvalues(edge, ns)
            if props:
                entry["properties"] = props
            edges.append(entry)

    save_graph_json({"nodes": nodes, "edges": edges}, json_path)


def _write_attvalues(parent: ET.Element, obj: dict[str, Any]) -> None:
    """Serialise non-core fields as GEXF ``attvalues``."""
    # Serialise any field that isn't already on the element (id/label/source/target)
    skip = {"id", "label", "source", "target"}
    props = obj.get("properties") if isinstance(obj.get("properties"), dict) else None
    items: list[tuple[str, Any]] = []
    if props:
        items.extend(props.items())
    else:
        items.extend((k, v) for k, v in obj.items() if k not in skip)
    if not items:
        return
    attvalues = ET.SubElement(parent, "attvalues")
    for key, value in items:
        ET.SubElement(attvalues, "attvalue", {"for": str(key), "value": str(value)})


def _read_attvalues(elem: ET.Element, ns: dict[str, str]) -> dict[str, str]:
    """Read GEXF ``attvalues`` back into a dict."""
    attvalues = elem.find(".//gexf:attvalues", ns) or elem.find(".//attvalues")
    if attvalues is None:
        return {}
    props: dict[str, str] = {}
    iter_av = attvalues.findall(".//gexf:attvalue", ns) or attvalues.findall(".//attvalue")
    for av in iter_av:
        key = av.get("for")
        value = av.get("value")
        if key and value is not None:
            props[key] = value
    return props


# ── JSON → Markdown ──────────────────────────────────────────────────


def json_to_markdown(json_path: PathLike, md_path: PathLike) -> None:
    """Convert a JSON graph to a human-readable Markdown rendering."""
    data = load_graph_json(json_path)

    labels = {n.get("id"): n.get("label", n.get("id")) for n in data["nodes"]}

    lines: list[str] = ["# Knowledge Graph\n", "\n", "## Nodes\n", "\n"]
    for node in data["nodes"]:
        label = node.get("label", node.get("id", ""))
        lines.append(f"### {label}\n")
        lines.append(f"- **ID**: {node.get('id', '')}\n")
        props = node.get("properties") if isinstance(node.get("properties"), dict) else None
        extra = props or {k: v for k, v in node.items() if k not in {"id", "label"}}
        if extra:
            lines.append("- **Properties**:\n")
            for k, v in extra.items():
                lines.append(f"  - {k}: {v}\n")
        lines.append("\n")

    lines.extend(["## Edges\n", "\n"])
    for edge in data["edges"]:
        src = labels.get(edge.get("source"), edge.get("source", ""))
        tgt = labels.get(edge.get("target"), edge.get("target", ""))
        relation = edge.get("label") or edge.get("mechanism") or "related to"
        lines.append(f"- **{src}** {relation} **{tgt}**\n")
        props = edge.get("properties") if isinstance(edge.get("properties"), dict) else None
        extra = props or {
            k: v for k, v in edge.items() if k not in {"source", "target", "label", "mechanism"}
        }
        for k, v in extra.items():
            lines.append(f"  - {k}: {v}\n")

    with Path(md_path).open("w", encoding="utf-8") as f:
        f.writelines(lines)


# ── Markdown → JSON (simple parser) ──────────────────────────────────


def markdown_to_json(md_path: PathLike, json_path: PathLike) -> None:
    """Parse a Markdown rendering (as produced by ``json_to_markdown``) back to JSON.

    Small parser: node headings are ``### Label`` with ``- **ID**: <id>``
    underneath; edges are bullets of the shape ``- **Source** relation **Target**``.
    """
    with Path(md_path).open(encoding="utf-8") as f:
        raw_lines = f.readlines()

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    current_id: str | None = None
    current_label: str | None = None
    in_nodes = in_edges = False

    for line in raw_lines:
        line = line.rstrip()
        if line.startswith("## Nodes"):
            in_nodes, in_edges = True, False
            continue
        if line.startswith("## Edges"):
            if current_id is not None:
                nodes.append({"id": current_id, "label": current_label or current_id})
                current_id = None
            in_nodes, in_edges = False, True
            continue
        if line.startswith("## "):
            in_nodes = in_edges = False
            continue

        if in_nodes:
            if line.startswith("### "):
                if current_id is not None:
                    nodes.append({"id": current_id, "label": current_label or current_id})
                current_label = line[4:].strip()
                current_id = current_label.lower().replace(" ", "_")
            elif line.startswith("- **ID**: "):
                current_id = line[len("- **ID**: ") :].strip()
        elif in_edges and line.startswith("- **") and "**" in line[4:]:
            parts = line[2:].split("**")
            if len(parts) >= 4:
                src_label = parts[1].strip()
                relation = parts[2].strip()
                tgt_label = parts[3].strip()
                edges.append(
                    {
                        "source": src_label.lower().replace(" ", "_"),
                        "target": tgt_label.lower().replace(" ", "_"),
                        "label": relation,
                    }
                )

    if current_id is not None:
        nodes.append({"id": current_id, "label": current_label or current_id})

    save_graph_json({"nodes": nodes, "edges": edges}, json_path)
