"""Tests for app.core.validation (S14-04).

Per invariant: one fixture that passes, one that fails. Plus an end-to-end
smoke test on the real sportdeelname_graph.json.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import networkx as nx

from app.core.dag_engine import CausalDAG
from app.core.validation import (
    ValidationReport,
    check_connectivity,
    detect_cycles,
    find_dangling_refs,
    find_duplicate_ids,
    find_orphan_nodes,
    validate_edge_weights,
    validate_graph,
)


def _v2_base() -> dict:
    """A minimal, structurally-clean v2 fixture used as a starting point."""
    return {
        "metadata": {"project": "val-fixture", "version": "0.0.0"},
        "nodes": [
            {"id": "A", "label": "A", "domain": "x", "level": "L0"},
            {"id": "B", "label": "B", "domain": "x", "level": "L0"},
            {"id": "C", "label": "C", "domain": "x", "level": "L1"},
        ],
        "edges": [
            {
                "id": "E1",
                "source": "A",
                "target": "B",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "STRUCTURAL",
            },
            {
                "id": "E2",
                "source": "B",
                "target": "C",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.7,
                "edge_type": "MEDIATING",
            },
        ],
    }


# ── detect_cycles ───────────────────────────────────────────────────


class TestDetectCycles:
    def test_no_cycles(self):
        dag = CausalDAG.from_dict(_v2_base())
        assert detect_cycles(dag.graph) == []

    def test_structural_cycle_reported(self):
        data = _v2_base()
        data["edges"].append(
            {
                "id": "E3",
                "source": "C",
                "target": "A",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "STRUCTURAL",
            }
        )
        # strict=False so we can inspect cycles via the validator
        dag = CausalDAG.from_dict(data, strict=False)
        cycles = detect_cycles(dag.graph)
        assert len(cycles) == 1
        assert set(cycles[0]) == {"A", "B", "C"}

    def test_feedback_cycle_ignored(self):
        """FEEDBACK edges are exempt from the acyclicity constraint."""
        data = _v2_base()
        data["edges"].append(
            {
                "id": "E3",
                "source": "C",
                "target": "A",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "FEEDBACK",
            }
        )
        dag = CausalDAG.from_dict(data)
        assert detect_cycles(dag.graph) == []


# ── find_orphan_nodes ───────────────────────────────────────────────


class TestFindOrphanNodes:
    def test_no_orphans(self):
        dag = CausalDAG.from_dict(_v2_base())
        assert find_orphan_nodes(dag.graph) == []

    def test_orphan_reported(self):
        data = _v2_base()
        data["nodes"].append(
            {"id": "ISOLATED", "label": "alone", "domain": "x", "level": "L0"}
        )
        dag = CausalDAG.from_dict(data)
        assert find_orphan_nodes(dag.graph) == ["ISOLATED"]


# ── find_duplicate_ids ──────────────────────────────────────────────


class TestFindDuplicateIds:
    def test_no_duplicates(self):
        node_dupes, edge_dupes = find_duplicate_ids(_v2_base())
        assert node_dupes == []
        assert edge_dupes == []

    def test_duplicate_node_id(self):
        data = _v2_base()
        data["nodes"].append(
            {"id": "A", "label": "A again", "domain": "x", "level": "L0"}
        )
        node_dupes, _ = find_duplicate_ids(data)
        assert node_dupes == ["A"]

    def test_duplicate_edge_id(self):
        data = _v2_base()
        dup = copy.deepcopy(data["edges"][0])
        dup["source"] = "B"
        dup["target"] = "C"
        data["edges"].append(dup)
        _, edge_dupes = find_duplicate_ids(data)
        assert edge_dupes == ["E1"]


# ── find_dangling_refs ──────────────────────────────────────────────


class TestFindDanglingRefs:
    def test_no_dangling(self):
        assert find_dangling_refs(_v2_base()) == []

    def test_dangling_target(self):
        data = _v2_base()
        data["edges"].append(
            {
                "id": "E3",
                "source": "A",
                "target": "DOES_NOT_EXIST",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "STRUCTURAL",
            }
        )
        dangling = find_dangling_refs(data)
        assert len(dangling) == 1
        assert dangling[0]["edge_id"] == "E3"
        assert dangling[0]["field"] == "target"
        assert dangling[0]["invalid_id"] == "DOES_NOT_EXIST"

    def test_dangling_moderator_target(self):
        """A moderator edge (target_type=edge) pointing to a missing edge id."""
        data = _v2_base()
        data["edges"].append(
            {
                "id": "E3",
                "source": "A",
                "target": "GHOST_EDGE",
                "target_type": "edge",
                "polarity": "moderator",
                "base_weight": 0.5,
                "edge_type": "MODERATOR",
            }
        )
        dangling = find_dangling_refs(data)
        assert len(dangling) == 1
        assert dangling[0]["field"] == "target(edge)"
        assert dangling[0]["invalid_id"] == "GHOST_EDGE"


# ── check_connectivity ──────────────────────────────────────────────


class TestCheckConnectivity:
    def test_single_component(self):
        dag = CausalDAG.from_dict(_v2_base())
        assert check_connectivity(dag.graph) == 1

    def test_multiple_components(self):
        data = _v2_base()
        data["nodes"].extend(
            [
                {"id": "X", "label": "X", "domain": "y", "level": "L0"},
                {"id": "Y", "label": "Y", "domain": "y", "level": "L0"},
            ]
        )
        data["edges"].append(
            {
                "id": "E3",
                "source": "X",
                "target": "Y",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "STRUCTURAL",
            }
        )
        dag = CausalDAG.from_dict(data)
        assert check_connectivity(dag.graph) == 2

    def test_empty_graph(self):
        g: nx.DiGraph = nx.DiGraph()
        assert check_connectivity(g) == 0


# ── validate_edge_weights ───────────────────────────────────────────


class TestValidateEdgeWeights:
    def test_valid_weights(self):
        dag = CausalDAG.from_dict(_v2_base())
        assert validate_edge_weights(dag.graph) == []

    def test_base_weight_out_of_range(self):
        """Pydantic catches this at load time (S14-02); the weights-checker
        catches it on already-loaded graphs that bypass strict validation."""
        data = _v2_base()
        data["edges"][0]["base_weight"] = 1.5
        # strict=False so we can still inspect graph-level edge attributes
        dag = CausalDAG.from_dict(data, strict=False)
        violations = validate_edge_weights(dag.graph)
        assert len(violations) == 1
        assert violations[0]["field"] == "base_weight"
        assert violations[0]["value"] == 1.5

    def test_strength_enum_unknown(self):
        """validate_edge_weights guards against non-enum strength strings
        that slipped through a non-strict load path (e.g. raw dicts added
        via ``graph.add_edge`` bypassing Pydantic). With strict=True,
        Pydantic itself rejects the value."""
        import networkx as nx

        g: nx.DiGraph = nx.DiGraph()
        g.add_node("A")
        g.add_node("B")
        g.add_edge(
            "A",
            "B",
            id="E1",
            strength="colossaal",
            base_weight=0.5,
        )
        violations = validate_edge_weights(g)
        assert any(v["field"] == "strength" for v in violations)


# ── validate_graph (orchestrator) ───────────────────────────────────


class TestValidateGraphOrchestrator:
    def test_clean_fixture_is_valid(self):
        report = validate_graph(_v2_base())
        assert isinstance(report, ValidationReport)
        assert report.is_valid is True
        assert report.node_count == 3
        assert report.edge_count == 2
        assert report.errors == []

    def test_dirty_fixture_reports_all_issues(self):
        """One fixture with multiple simultaneous violations."""
        data = _v2_base()
        # Duplicate node id
        data["nodes"].append(
            {"id": "A", "label": "dup", "domain": "x", "level": "L0"}
        )
        # Orphan node
        data["nodes"].append(
            {"id": "Z", "label": "alone", "domain": "x", "level": "L0"}
        )
        # Dangling target
        data["edges"].append(
            {
                "id": "E99",
                "source": "A",
                "target": "MISSING",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": "STRUCTURAL",
            }
        )
        # Invalid base_weight
        data["edges"][0]["base_weight"] = 2.0

        report = validate_graph(data)
        assert report.is_valid is False
        assert "A" in report.duplicate_node_ids
        assert "Z" in report.orphan_nodes
        assert any(d["invalid_id"] == "MISSING" for d in report.dangling_refs)
        assert any(
            v["field"] == "base_weight" and v["value"] == 2.0
            for v in report.edge_weight_violations
        )
        # Summary prints without crashing
        assert "INVALID" in report.summary()

    def test_report_to_dict_roundtrip(self):
        report = validate_graph(_v2_base())
        d = report.to_dict()
        assert d["is_valid"] is True
        assert d["node_count"] == 3
        # JSON-serialisable
        json.dumps(d)


# ── Real-data smoke test ────────────────────────────────────────────


class TestRealData:
    """Informational: what does the validator say about the actual model?"""

    def test_sportdeelname_graph_is_valid(self):
        path = Path("data/models/sportdeelname_graph.json")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        report = validate_graph(data)
        # Expectation: the shipped model is valid. If this fails, the message
        # will show the actual errors — update the model or the checks.
        assert report.is_valid, (
            f"sportdeelname_graph.json no longer valid:\n{report.summary()}"
        )
