"""Format conversion tests (JSON ↔ GEXF ↔ Markdown) for the consolidated
``app.core.graph_io`` module — S14-02.

Replaces the historical ``tests/test_conversions.py`` that exercised the
retired ``graaf_zeppelin/knowledge_graph.py``. The conversions now
operate on dicts directly; no intermediate class is involved.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.graph_io import (
    gexf_to_json,
    json_to_gexf,
    json_to_markdown,
    load_graph_json,
    markdown_to_json,
    save_graph_json,
)


@pytest.fixture
def tmp_output(tmp_path: Path) -> Path:
    """pytest-managed temporary directory."""
    return tmp_path


def _simple_graph() -> dict:
    return {
        "nodes": [
            {"id": "n1", "label": "Node 1", "properties": {"type": "test"}},
            {"id": "n2", "label": "Node 2"},
        ],
        "edges": [
            {"source": "n1", "target": "n2", "label": "connects to"},
        ],
    }


def test_json_roundtrip(tmp_output: Path) -> None:
    path = tmp_output / "g.json"
    save_graph_json(_simple_graph(), path)
    data = load_graph_json(path)
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["nodes"][0]["label"] == "Node 1"


def test_utf8_encoding(tmp_output: Path) -> None:
    g = {
        "nodes": [
            {
                "id": "café",
                "label": "Café ☕",
                "properties": {"description": "Gezellig"},
            },
            {
                "id": "über",
                "label": "Über 🎵",
                "properties": {"description": "Dvorák"},
            },
        ],
        "edges": [
            {"source": "café", "target": "über", "label": "heeft éèêë"},
        ],
    }
    path = tmp_output / "utf8.json"
    save_graph_json(g, path)
    data = load_graph_json(path)
    assert data["nodes"][0]["id"] == "café"
    assert "☕" in data["nodes"][0]["label"]
    assert "Dvorák" in data["nodes"][1]["properties"]["description"]


def test_json_to_gexf(tmp_output: Path) -> None:
    json_path = tmp_output / "g.json"
    gexf_path = tmp_output / "g.gexf"
    save_graph_json(_simple_graph(), json_path)

    json_to_gexf(json_path, gexf_path)

    content = gexf_path.read_text(encoding="utf-8")
    assert "Node 1" in content
    assert "n1" in content
    assert "connects to" in content


def test_gexf_to_json_roundtrip(tmp_output: Path) -> None:
    src_json = tmp_output / "src.json"
    gexf = tmp_output / "mid.gexf"
    dst_json = tmp_output / "dst.json"
    save_graph_json(_simple_graph(), src_json)

    json_to_gexf(src_json, gexf)
    gexf_to_json(gexf, dst_json)

    data = load_graph_json(dst_json)
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["nodes"][0]["label"] == "Node 1"


def test_json_to_markdown(tmp_output: Path) -> None:
    json_path = tmp_output / "g.json"
    md_path = tmp_output / "g.md"
    save_graph_json(_simple_graph(), json_path)

    json_to_markdown(json_path, md_path)

    text = md_path.read_text(encoding="utf-8")
    assert "# Knowledge Graph" in text
    assert "## Nodes" in text
    assert "## Edges" in text
    assert "Node 1" in text
    assert "connects to" in text


def test_markdown_to_json(tmp_output: Path) -> None:
    md = (
        "# Knowledge Graph\n\n"
        "## Nodes\n\n"
        "### Python\n- **ID**: python\n\n"
        "### Data Science\n- **ID**: data\n\n"
        "## Edges\n\n"
        "- **Python** used in **Data Science**\n"
    )
    md_path = tmp_output / "g.md"
    json_path = tmp_output / "g.json"
    md_path.write_text(md, encoding="utf-8")

    markdown_to_json(md_path, json_path)

    data = load_graph_json(json_path)
    assert len(data["nodes"]) == 2
    assert data["nodes"][0]["id"] == "python"
    assert data["edges"][0]["label"] == "used in"


def test_load_graph_json_shape_checks(tmp_output: Path) -> None:
    """load_graph_json normalises the shape: nodes/edges default to []."""
    path = tmp_output / "empty.json"
    path.write_text("{}", encoding="utf-8")
    data = load_graph_json(path)
    assert data["nodes"] == []
    assert data["edges"] == []

    bad = tmp_output / "bad.json"
    bad.write_text('{"nodes": "not a list"}', encoding="utf-8")
    with pytest.raises(ValueError, match="'nodes' must be a list"):
        load_graph_json(bad)

    nondict = tmp_output / "nondict.json"
    nondict.write_text('["a", "b"]', encoding="utf-8")
    with pytest.raises(ValueError, match="dict"):
        load_graph_json(nondict)
