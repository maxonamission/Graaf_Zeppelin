"""Tests for the prompt builder."""

from app.core.dag_engine import CausalDAG
from app.core.prompt_builder import PromptBuilder


def make_test_dag() -> CausalDAG:
    dag = CausalDAG(
        name="Sportdeelname",
        version="1.0.0",
        description="Test model voor sportdeelname",
    )
    dag.add_factor("motivatie", label="Motivatie", description="Intrinsieke motivatie")
    dag.add_factor("sportdeelname", label="Sportdeelname", description="Deelname aan sport")
    dag.add_factor("coaching", label="Coaching", description="Kwaliteit begeleiding")
    dag.add_relation("motivatie", "sportdeelname", direction="positive", strength=0.9)
    dag.add_relation("coaching", "motivatie", direction="positive", strength=0.7)
    return dag


class TestPromptBuilder:
    def test_system_prompt_contains_model_info(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        prompt = builder.build_system_prompt()
        assert "Sportdeelname" in prompt
        assert "1.0.0" in prompt
        assert "causale" in prompt.lower()

    def test_query_prompt_with_factors(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        prompt = builder.build_query_prompt("Wat is de rol van coaching?", factor_ids=["coaching"])
        assert "Coaching" in prompt
        assert "Motivatie" in prompt  # coaching affects motivatie

    def test_query_prompt_without_factors(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        prompt = builder.build_query_prompt("Algemene vraag")
        assert "Motivatie" in prompt
        assert "Sportdeelname" in prompt
        assert "Coaching" in prompt

    def test_full_prompt_returns_messages(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        messages = builder.build_full_prompt("Test vraag")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"

    def test_intervention_prompt(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        prompt = builder.build_intervention_prompt("coaching", 0.2)
        assert "Coaching" in prompt
        assert "toename" in prompt
        assert "20%" in prompt

    def test_intervention_prompt_negative(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        prompt = builder.build_intervention_prompt("coaching", -0.3)
        assert "afname" in prompt
        assert "30%" in prompt

    def test_intervention_invalid_factor(self):
        dag = make_test_dag()
        builder = PromptBuilder(dag)
        try:
            builder.build_intervention_prompt("nonexistent", 0.2)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass
