"""Tests for app.core.graph_models (S14-02).

Per category: one fixture that passes, one that fails with a clear
ValidationError. Plus a round-trip test on the real
sportdeelname_graph.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.graph_models import (
    BondInfluence,
    CurveType,
    Edge,
    EdgeType,
    Graph,
    Node,
    NodeStatus,
    Polarity,
    Strength,
    TargetType,
)


def _valid_graph_data() -> dict:
    return {
        "metadata": {"project": "test", "version": "0.0.0"},
        "nodes": [
            {
                "id": "A",
                "label": "Alpha",
                "domain": "Uitkomsten",
                "level": "L0",
                "bond_influence": "none",
                "status": "A",
            },
            {
                "id": "B",
                "label": "Beta",
                "domain": "Psychologisch",
                "level": "L1",
                "bond_influence": "medium",
                "status": "-",
            },
        ],
        "edges": [
            {
                "id": "E1",
                "source": "A",
                "target": "B",
                "polarity": "positief",
                "strength": "sterk",
                "base_weight": 0.8,
                "edge_type": "STRUCTURAL",
                "curve_type": "LINEAR",
            }
        ],
    }


# ── Enum normalisation ──────────────────────────────────────────────


class TestEnums:
    def test_polarity_nl_values_accepted(self):
        for v in ("positief", "negatief", "variabel", "moderator"):
            e = Edge(source="A", target="B", polarity=v)
            assert e.polarity == v

    def test_polarity_english_alias_normalised(self):
        e = Edge(source="A", target="B", polarity="positive")
        assert e.polarity == "positief"

    def test_strength_english_alias_normalised(self):
        e = Edge(source="A", target="B", strength="strong")
        assert e.strength == "sterk"

    def test_empty_string_becomes_none(self):
        """The data uses "" for unset optional enums; Pydantic normalises."""
        e = Edge(source="A", target="B", curve_type="", edge_type="")
        assert e.curve_type is None
        assert e.edge_type is None

    def test_unknown_polarity_rejected(self):
        with pytest.raises(ValidationError, match="polarity"):
            Edge(source="A", target="B", polarity="amusant")


# ── base_weight range ───────────────────────────────────────────────


class TestBaseWeight:
    def test_valid_weight(self):
        e = Edge(source="A", target="B", base_weight=0.5)
        assert e.base_weight == 0.5

    def test_weight_above_one(self):
        with pytest.raises(ValidationError, match="base_weight"):
            Edge(source="A", target="B", base_weight=1.5)

    def test_weight_below_zero(self):
        with pytest.raises(ValidationError, match="base_weight"):
            Edge(source="A", target="B", base_weight=-0.1)


# ── Required fields ─────────────────────────────────────────────────


class TestRequiredFields:
    def test_node_requires_id(self):
        with pytest.raises(ValidationError, match="id"):
            Node()  # type: ignore[call-arg]

    def test_edge_requires_source_and_target(self):
        with pytest.raises(ValidationError):
            Edge()  # type: ignore[call-arg]

    def test_node_accepts_extra_fields(self):
        """``extra="allow"`` so data-side additions don't break the loader."""
        n = Node(id="X", some_future_field="whatever")
        assert n.id == "X"


# ── Graph-level dangling-ref check ──────────────────────────────────


class TestDanglingRefs:
    def test_valid_graph(self):
        g = Graph.model_validate(_valid_graph_data())
        assert len(g.nodes) == 2
        assert len(g.edges) == 1

    def test_source_missing(self):
        data = _valid_graph_data()
        data["edges"][0]["source"] = "DOES_NOT_EXIST"
        with pytest.raises(ValidationError, match="source"):
            Graph.model_validate(data)

    def test_target_missing(self):
        data = _valid_graph_data()
        data["edges"][0]["target"] = "DOES_NOT_EXIST"
        with pytest.raises(ValidationError, match="target"):
            Graph.model_validate(data)

    def test_moderator_edge_target_must_be_existing_edge(self):
        data = _valid_graph_data()
        data["edges"].append(
            {
                "id": "E2",
                "source": "A",
                "target": "GHOST",
                "target_type": "edge",
                "edge_type": "MODERATOR",
                "polarity": "moderator",
            }
        )
        with pytest.raises(ValidationError, match="moderator target"):
            Graph.model_validate(data)

    def test_moderator_edge_valid(self):
        """An edge id that exists is accepted as moderator target."""
        data = _valid_graph_data()
        data["edges"].append(
            {
                "id": "E2",
                "source": "A",
                "target": "E1",  # existing edge
                "target_type": "edge",
                "edge_type": "MODERATOR",
                "polarity": "moderator",
            }
        )
        g = Graph.model_validate(data)
        assert len(g.edges) == 2


# ── Round-trip on real data ─────────────────────────────────────────


class TestRealDataRoundtrip:
    def test_sportdeelname_loads_cleanly(self):
        path = Path("data/models/sportdeelname_graph.json")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        g = Graph.model_validate(data)
        assert len(g.nodes) == 69
        assert len(g.edges) == 114

    def test_roundtrip_preserves_semantics(self):
        path = Path("data/models/sportdeelname_graph.json")
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        g = Graph.model_validate(data)
        dumped = g.model_dump(mode="json")
        # Re-validate the dumped form; equality on counts and ids
        g2 = Graph.model_validate(dumped)
        assert {n.id for n in g2.nodes} == {n.id for n in g.nodes}
        assert len(g2.edges) == len(g.edges)


# ── Enum exports ────────────────────────────────────────────────────


class TestEnumExports:
    """Confirms public enum members are available for downstream use."""

    def test_enums_have_expected_members(self):
        assert Polarity.POSITIEF == "positief"
        assert Strength.STERK == "sterk"
        assert EdgeType.FEEDBACK == "FEEDBACK"
        assert CurveType.LINEAR == "LINEAR"
        assert BondInfluence.HIGH == "high"
        assert NodeStatus.A == "A"
        assert TargetType.EDGE == "edge"

    def test_time_lag_removed(self):
        """S14-03 Pad B: the TimeLag enum is no longer exported."""
        import app.core.graph_models as gm

        assert not hasattr(gm, "TimeLag")
        # The Edge model no longer carries a time_lag field either
        assert "time_lag" not in Edge.model_fields
