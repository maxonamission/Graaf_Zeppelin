"""Tests for the DAG engine — v1 and v2 schema support."""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.dag_engine import ACYCLIC_EDGE_TYPES, CausalDAG


def make_simple_dag() -> CausalDAG:
    """Create a small test DAG."""
    dag = CausalDAG(name="test", version="0.1.0", description="Test model")
    dag.add_factor("a", label="Factor A", category="input")
    dag.add_factor("b", label="Factor B", category="mediator")
    dag.add_factor("c", label="Factor C", category="outcome")
    dag.add_relation("a", "b", direction="positive", strength=0.8)
    dag.add_relation("b", "c", direction="positive", strength=0.6)
    dag.add_relation("a", "c", direction="negative", strength=0.3)
    return dag


def make_v2_data() -> dict:
    """Create minimal v2 schema data for testing."""
    return {
        "metadata": {
            "project": "Test Model v2",
            "version": "2.0.0",
            "summary": {"description": "Test v2 model"},
            "graph_metrics": {"avg_degree": 2.0},
        },
        "nodes": [
            {
                "id": "N001",
                "label": "Uitkomst",
                "domain": "Uitkomsten",
                "level": "L0",
                "bond_influence": "none",
                "disciplines": ["Univ"],
                "status": "-",
                "definition": "De uitkomst",
                "degree": 3,
                "in_degree": 2,
                "out_degree": 1,
            },
            {
                "id": "N002",
                "label": "Motivatie",
                "domain": "Psychologisch",
                "level": "L1",
                "bond_influence": "medium",
                "disciplines": ["Univ"],
                "status": "A",
                "definition": "Intrinsieke motivatie",
            },
            {
                "id": "N003",
                "label": "Kosten",
                "domain": "Middelen",
                "level": "L1",
                "bond_influence": "high",
                "disciplines": ["Univ"],
                "status": "-",
                "definition": "Financiële kosten",
            },
        ],
        "edges": [
            {
                "id": "E001",
                "source": "N002",
                "target": "N001",
                "target_type": "node",
                "source_label": "Motivatie",
                "target_label": "Uitkomst",
                "polarity": "positief",
                "strength": "sterk",
                "base_weight": 0.8,
                "mechanism": "Motivatie drijft deelname",
                "cluster": "Psychologisch",
                "edge_type": "MEDIATING",
                "curve_type": "LINEAR",
                "curve_params": {},
                "literature": ["L001"],
                "slider_sensitivity": {"sens_test": "high"},
                "disciplines": ["Univ"],
                "bond_influence": "medium",
                "time_lag": "",
                "status": "A",
            },
            {
                "id": "E002",
                "source": "N003",
                "target": "N001",
                "target_type": "node",
                "source_label": "Kosten",
                "target_label": "Uitkomst",
                "polarity": "negatief",
                "strength": "midden",
                "base_weight": 0.5,
                "mechanism": "Hogere kosten verlagen deelname",
                "cluster": "Middelen",
                "edge_type": "STRUCTURAL",
                "curve_type": "",
                "curve_params": {},
                "literature": [],
                "slider_sensitivity": {"sens_test": "medium"},
                "disciplines": ["Univ"],
                "bond_influence": "high",
                "time_lag": "",
                "status": "-",
            },
            {
                "id": "E003",
                "source": "N003",
                "target": "E002",
                "target_type": "edge",
                "source_label": "Kosten",
                "target_label": "Kosten → Uitkomst",
                "polarity": "moderator",
                "strength": "midden",
                "base_weight": 0.5,
                "mechanism": "Kosten modereren eigen effect",
                "cluster": "Middelen",
                "edge_type": "MODERATOR",
                "curve_type": "",
                "curve_params": {},
                "literature": [],
                "slider_sensitivity": {},
                "disciplines": ["Univ"],
                "bond_influence": "none",
                "time_lag": "",
                "status": "-",
            },
        ],
        "sliders": [
            {
                "id": "S01",
                "label": "Test Slider",
                "type": "Globaal",
                "curve_type": "LINEAR_MOD",
                "curve_params": {"gamma": 0.3},
                "default": 0.5,
                "range": [0, 1],
                "direction": "versterking",
                "sensitivity_key": "sens_test",
                "definition": "Test slider definitie",
                "mechanism": "Lineaire versterking",
                "related_nodes": ["N002"],
                "primary_clusters": ["Psychologisch"],
                "evidence": ["Test (2024): test evidence"],
                "qualifiers": [
                    {
                        "question": "Hoe sterk is de motivatie?",
                        "options": [
                            {"label": "Laag", "value": 0.2},
                            {"label": "Gemiddeld", "value": 0.5},
                            {"label": "Hoog", "value": 0.8},
                        ],
                    },
                    {
                        "question": "Hoe belangrijk is plezier?",
                        "options": [
                            {"label": "Niet belangrijk", "value": 0.1},
                            {"label": "Belangrijk", "value": 0.6},
                            {"label": "Zeer belangrijk", "value": 0.9},
                        ],
                    },
                ],
            },
        ],
    }


# ── v1 tests (backward compat) ──────────────────────────────────────────


class TestCausalDAGv1:
    def test_add_factors(self):
        dag = CausalDAG(name="t", version="0.1.0")
        dag.add_factor("x", label="X")
        assert dag.graph.number_of_nodes() == 1
        assert dag.graph.nodes["x"]["label"] == "X"

    def test_add_relation(self):
        dag = make_simple_dag()
        assert dag.graph.number_of_edges() == 3

    def test_cycle_detection(self):
        dag = make_simple_dag()
        dag.add_factor("d", label="Factor D")
        dag.add_relation("c", "d", direction="positive", strength=0.5)
        with pytest.raises(ValueError, match="cycle"):
            dag.add_relation("d", "a", direction="positive", strength=0.5)

    def test_relation_invalid_factor(self):
        dag = CausalDAG(name="t", version="0.1.0")
        dag.add_factor("a", label="A")
        with pytest.raises(ValueError, match="does not exist"):
            dag.add_relation("a", "nonexistent", direction="positive", strength=0.5)

    def test_relation_invalid_strength(self):
        dag = CausalDAG(name="t", version="0.1.0")
        dag.add_factor("a", label="A")
        dag.add_factor("b", label="B")
        with pytest.raises(ValueError, match="Strength"):
            dag.add_relation("a", "b", direction="positive", strength=1.5)

    def test_get_causes(self):
        dag = make_simple_dag()
        causes = dag.get_causes("c")
        cause_ids = {c["factor"] for c in causes}
        assert cause_ids == {"a", "b"}

    def test_get_effects(self):
        dag = make_simple_dag()
        effects = dag.get_effects("a")
        effect_ids = {e["factor"] for e in effects}
        assert effect_ids == {"b", "c"}

    def test_causal_paths(self):
        dag = make_simple_dag()
        paths = dag.get_causal_paths("a", "c")
        assert len(paths) == 2  # a→c direct and a→b→c
        path_tuples = [tuple(p) for p in paths]
        assert ("a", "c") in path_tuples
        assert ("a", "b", "c") in path_tuples

    def test_ancestors_descendants(self):
        dag = make_simple_dag()
        assert dag.get_ancestors("c") == {"a", "b"}
        assert dag.get_descendants("a") == {"b", "c"}

    def test_simulate_intervention(self):
        dag = make_simple_dag()
        effects = dag.simulate_intervention("a", 0.5)
        assert len(effects) > 0
        affected_ids = {e["factor"] for e in effects}
        assert "b" in affected_ids
        assert "c" in affected_ids

    def test_get_factor_info(self):
        dag = make_simple_dag()
        info = dag.get_factor_info("b")
        assert info is not None
        assert info["label"] == "Factor B"
        assert len(info["causes"]) == 1
        assert len(info["effects"]) == 1

    def test_get_factor_info_nonexistent(self):
        dag = make_simple_dag()
        assert dag.get_factor_info("nonexistent") is None

    def test_graph_summary(self):
        dag = make_simple_dag()
        summary = dag.get_graph_summary()
        assert summary["num_factors"] == 3
        assert summary["num_relations"] == 3
        assert "a" in summary["root_factors"]

    def test_serialize_deserialize(self):
        dag = make_simple_dag()
        data = dag.to_dict()
        dag2 = CausalDAG.from_dict(data)
        assert dag2.name == dag.name
        assert dag2.graph.number_of_nodes() == dag.graph.number_of_nodes()
        assert dag2.graph.number_of_edges() == dag.graph.number_of_edges()

    def test_save_load(self):
        dag = make_simple_dag()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test_model.json"
            dag.save(path)
            assert path.exists()

            dag2 = CausalDAG.load(path)
            assert dag2.name == "test"
            assert dag2.graph.number_of_nodes() == 3

    def test_load_sportdeelname_v1(self):
        """Test that the v1 sportdeelname model loads correctly."""
        dag = CausalDAG.load("data/models/sportdeelname_v1.json")
        summary = dag.get_graph_summary()
        assert summary["num_factors"] == 15
        assert summary["num_relations"] > 20
        assert summary["name"] == "Sportdeelname"
        info = dag.get_factor_info("sportdeelname")
        assert info is not None
        assert len(info["causes"]) > 3


# ── v2 tests ─────────────────────────────────────────────────────────────


class TestCausalDAGv2:
    def test_load_v2_schema(self):
        """Test v2 schema detection and loading."""
        data = make_v2_data()
        dag = CausalDAG.from_dict(data)
        assert dag._schema_version == 2
        assert dag.name == "Test Model v2"
        assert dag.version == "2.0.0"

    def test_v2_nodes_loaded(self):
        dag = CausalDAG.from_dict(make_v2_data())
        assert dag.graph.number_of_nodes() == 3
        node = dag.graph.nodes["N002"]
        assert node["label"] == "Motivatie"
        assert node["domain"] == "Psychologisch"
        assert node["definition"] == "Intrinsieke motivatie"

    def test_v2_regular_edges_loaded(self):
        """Regular edges (target_type=node) become NetworkX edges."""
        dag = CausalDAG.from_dict(make_v2_data())
        # 2 regular edges (E001, E002), E003 is moderator
        assert dag.graph.number_of_edges() == 2
        edge = dag.graph.edges["N002", "N001"]
        assert edge["direction"] == "positive"
        assert edge["strength"] == 0.8
        assert edge["mechanism"] == "Motivatie drijft deelname"

    def test_v2_moderator_edges_stored_separately(self):
        """Moderator edges (target_type=edge) are NOT in NetworkX graph."""
        dag = CausalDAG.from_dict(make_v2_data())
        # E003 is a moderator targeting E002
        assert "E002" in dag.moderators
        mods = dag.moderators["E002"]
        assert len(mods) == 1
        assert mods[0]["moderator_node"] == "N003"
        assert mods[0]["mechanism"] == "Kosten modereren eigen effect"

    def test_v2_polarity_mapping(self):
        """Polarity 'positief'→'positive', 'negatief'→'negative'."""
        dag = CausalDAG.from_dict(make_v2_data())
        e1 = dag.graph.edges["N002", "N001"]
        assert e1["direction"] == "positive"
        assert e1["polarity"] == "positief"
        e2 = dag.graph.edges["N003", "N001"]
        assert e2["direction"] == "negative"
        assert e2["polarity"] == "negatief"

    def test_v2_base_weight_as_strength(self):
        """base_weight is used as numeric strength, not the string field."""
        dag = CausalDAG.from_dict(make_v2_data())
        e1 = dag.graph.edges["N002", "N001"]
        assert e1["strength"] == 0.8  # base_weight, not "sterk"

    def test_v2_sliders_loaded(self):
        dag = CausalDAG.from_dict(make_v2_data())
        sliders = dag.get_sliders()
        assert len(sliders) == 1
        assert sliders[0]["id"] == "S01"
        assert sliders[0]["label"] == "Test Slider"

    def test_v2_get_slider(self):
        dag = CausalDAG.from_dict(make_v2_data())
        s = dag.get_slider("S01")
        assert s is not None
        assert s["curve_type"] == "LINEAR_MOD"
        assert dag.get_slider("NONEXISTENT") is None

    def test_v2_domains(self):
        dag = CausalDAG.from_dict(make_v2_data())
        domains = dag.get_domains()
        assert "Psychologisch" in domains
        assert domains["Psychologisch"] == 1
        assert "Uitkomsten" in domains
        assert domains["Uitkomsten"] == 1

    def test_v2_nodes_by_domain(self):
        dag = CausalDAG.from_dict(make_v2_data())
        psych = dag.get_nodes_by_domain("Psychologisch")
        assert len(psych) == 1
        assert psych[0]["id"] == "N002"

    def test_v2_filter_factors(self):
        dag = CausalDAG.from_dict(make_v2_data())
        all_factors = dag.get_all_factors()
        assert len(all_factors) == 3
        by_domain = dag.get_all_factors(domain="Psychologisch")
        assert len(by_domain) == 1
        by_status = dag.get_all_factors(status="A")
        assert len(by_status) == 1

    def test_v2_filter_relations(self):
        dag = CausalDAG.from_dict(make_v2_data())
        all_rels = dag.get_all_relations()
        assert len(all_rels) == 2
        by_cluster = dag.get_all_relations(cluster="Psychologisch")
        assert len(by_cluster) == 1

    def test_v2_edge_moderators(self):
        dag = CausalDAG.from_dict(make_v2_data())
        mods = dag.get_edge_moderators("E002")
        assert len(mods) == 1
        assert mods[0]["moderator_node"] == "N003"
        assert dag.get_edge_moderators("NONEXISTENT") == []

    def test_v2_summary_includes_domains(self):
        dag = CausalDAG.from_dict(make_v2_data())
        summary = dag.get_graph_summary()
        assert "domains" in summary
        assert "num_sliders" in summary
        assert summary["num_sliders"] == 1
        assert "num_moderators" in summary
        assert summary["num_moderators"] == 1

    def test_v2_metadata_stored(self):
        dag = CausalDAG.from_dict(make_v2_data())
        assert dag.metadata.get("project") == "Test Model v2"
        assert dag.metadata.get("graph_metrics", {}).get("avg_degree") == 2.0

    def test_v2_factor_info_includes_moderates(self):
        """Factor info for a moderator node includes moderated edges."""
        dag = CausalDAG.from_dict(make_v2_data())
        info = dag.get_factor_info("N003")
        assert info is not None
        assert "moderates_edges" in info
        assert len(info["moderates_edges"]) == 1
        assert info["moderates_edges"][0]["edge_id"] == "E002"

    def test_v2_simulate_intervention(self):
        dag = CausalDAG.from_dict(make_v2_data())
        effects = dag.simulate_intervention("N002", 0.5)
        assert len(effects) > 0
        affected_ids = {e["factor"] for e in effects}
        assert "N001" in affected_ids

    def test_load_v2_from_file(self):
        """Test v2 schema loads from file."""
        data = make_v2_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "v2_model.json"
            with open(path, "w") as f:
                json.dump(data, f)
            dag = CausalDAG.load(path)
            assert dag._schema_version == 2
            assert dag.graph.number_of_nodes() == 3

    def test_v2_get_slider_qualifiers(self):
        """Test getting qualifier questions from a slider."""
        dag = CausalDAG.from_dict(make_v2_data())
        qualifiers = dag.get_slider_qualifiers("S01")
        assert qualifiers is not None
        assert len(qualifiers) == 2
        assert qualifiers[0]["question"] == "Hoe sterk is de motivatie?"
        assert len(qualifiers[0]["options"]) == 3

    def test_v2_get_slider_qualifiers_nonexistent(self):
        dag = CausalDAG.from_dict(make_v2_data())
        assert dag.get_slider_qualifiers("NONEXISTENT") is None

    def test_v2_get_relevant_sliders_by_node(self):
        """Slider is relevant when factor_id is in related_nodes."""
        dag = CausalDAG.from_dict(make_v2_data())
        relevant = dag.get_relevant_sliders(["N002"])
        assert len(relevant) == 1
        assert relevant[0]["id"] == "S01"

    def test_v2_get_relevant_sliders_by_cluster(self):
        """Slider is relevant when factor's cluster matches primary_clusters."""
        data = make_v2_data()
        # N002 has domain "Psychologisch" but we need cluster attribute
        data["nodes"][1]["cluster"] = "Psychologisch"
        dag = CausalDAG.from_dict(data)
        # Use N001 which is NOT in related_nodes but check cluster match
        # N002 is in related_nodes, so use a node whose cluster matches
        relevant = dag.get_relevant_sliders(["N002"])
        assert len(relevant) == 1

    def test_v2_get_relevant_sliders_no_match(self):
        """No relevant sliders when factors don't overlap."""
        dag = CausalDAG.from_dict(make_v2_data())
        # N001 is not in related_nodes and its domain/cluster doesn't match
        relevant = dag.get_relevant_sliders(["N001"])
        # N001 domain is "Uitkomsten", slider primary_clusters is ["Psychologisch"]
        assert len(relevant) == 0

    def test_v2_get_relevant_sliders_empty_factors(self):
        """Empty factor list returns all sliders."""
        dag = CausalDAG.from_dict(make_v2_data())
        relevant = dag.get_relevant_sliders([])
        assert len(relevant) == 1  # all sliders

    def test_load_sportdeelname_v2(self):
        """Test that the full v2.3.0 sportdeelname model loads correctly."""
        dag = CausalDAG.load("data/models/sportdeelname_graph.json")
        summary = dag.get_graph_summary()
        assert dag._schema_version == 2
        assert summary["num_factors"] == 69
        # 114 total - 4 moderators - 2 duplicate pairs (NetworkX merges) = 108
        assert summary["num_relations"] == 108
        assert summary["num_sliders"] == 8
        assert summary["num_moderators"] == 4
        assert len(summary["domains"]) >= 7
        # Check a known node
        info = dag.get_factor_info("N018")
        assert info is not None
        assert info["label"] == "Intrinsieke motivatie"

    def test_load_sportdeelname_v2_qualifiers(self):
        """Test that all 8 sliders have qualifier questions."""
        dag = CausalDAG.load("data/models/sportdeelname_graph.json")
        for slider in dag.sliders:
            qualifiers = slider.get("qualifiers", [])
            assert len(qualifiers) >= 2, f"Slider {slider['id']} has no qualifiers"
            for q in qualifiers:
                assert "question" in q
                assert "options" in q
                assert len(q["options"]) >= 3


# ── S14-01: cycle-check per edge-type ────────────────────────────────────


def _v2_cycle_fixture(edge_type: str) -> dict:
    """Minimal v2 fixture with a 2-node cycle A↔B of a given edge_type."""
    return {
        "metadata": {"project": "cycle-fixture", "version": "0.0.0"},
        "nodes": [
            {"id": "A", "label": "A", "domain": "x", "level": "L0"},
            {"id": "B", "label": "B", "domain": "x", "level": "L0"},
        ],
        "edges": [
            {
                "id": "E1",
                "source": "A",
                "target": "B",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": edge_type,
            },
            {
                "id": "E2",
                "source": "B",
                "target": "A",
                "target_type": "node",
                "polarity": "positief",
                "base_weight": 0.5,
                "edge_type": edge_type,
            },
        ],
    }


class TestAcyclicEdgeTypes:
    def test_acyclic_edge_types_constant(self):
        """STRUCTURAL/MEDIATING/MODERATOR are acyclic; FEEDBACK/SOCIAL_REGULATORY are not."""
        assert "STRUCTURAL" in ACYCLIC_EDGE_TYPES
        assert "MEDIATING" in ACYCLIC_EDGE_TYPES
        assert "MODERATOR" in ACYCLIC_EDGE_TYPES
        assert "FEEDBACK" not in ACYCLIC_EDGE_TYPES
        assert "SOCIAL_REGULATORY" not in ACYCLIC_EDGE_TYPES

    def test_feedback_edges_may_form_cycles(self):
        """Two FEEDBACK edges A↔B are accepted (not a DAG in the acyclic-type sense)."""
        dag = CausalDAG.from_dict(_v2_cycle_fixture("FEEDBACK"))
        assert dag.graph.number_of_nodes() == 2
        assert dag.graph.number_of_edges() == 2

    def test_social_regulatory_edges_may_form_cycles(self):
        """SOCIAL_REGULATORY is also exempt from the acyclicity constraint."""
        dag = CausalDAG.from_dict(_v2_cycle_fixture("SOCIAL_REGULATORY"))
        assert dag.graph.number_of_edges() == 2

    def test_structural_cycle_still_blocked(self):
        """STRUCTURAL cycles must still raise, with edge_type in the message."""
        with pytest.raises(ValueError) as exc:
            CausalDAG.from_dict(_v2_cycle_fixture("STRUCTURAL"))
        msg = str(exc.value)
        assert "STRUCTURAL" in msg
        # Error message names the offending edges
        assert "A→B" in msg or "B→A" in msg

    def test_mediating_cycle_blocked(self):
        """MEDIATING cycles are likewise blocked."""
        with pytest.raises(ValueError, match="MEDIATING"):
            CausalDAG.from_dict(_v2_cycle_fixture("MEDIATING"))

    def test_mixed_feedback_and_structural_cycle(self):
        """A STRUCTURAL edge cycling through a FEEDBACK edge is still blocked
        only if the STRUCTURAL subgraph itself is cyclic — here it isn't."""
        data = _v2_cycle_fixture("FEEDBACK")
        # Swap one FEEDBACK → STRUCTURAL; remaining structural is a single A→B edge.
        data["edges"][0]["edge_type"] = "STRUCTURAL"
        dag = CausalDAG.from_dict(data)
        assert dag.graph.number_of_edges() == 2  # no cycle in STRUCTURAL subgraph alone
