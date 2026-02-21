"""Tests for the DAG engine."""

import json
import tempfile
from pathlib import Path

import pytest

from app.core.dag_engine import CausalDAG


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


class TestCausalDAG:
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
        # Check that factor B is affected
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

    def test_load_sportdeelname_model(self):
        """Test that the actual sportdeelname model loads correctly."""
        dag = CausalDAG.load("data/models/sportdeelname_v1.json")
        summary = dag.get_graph_summary()
        assert summary["num_factors"] == 15
        assert summary["num_relations"] > 20
        assert summary["name"] == "Sportdeelname"
        # Sportdeelname should not be a root (gezondheid feeds into it)
        # but it should have many causes
        info = dag.get_factor_info("sportdeelname")
        assert info is not None
        assert len(info["causes"]) > 3
