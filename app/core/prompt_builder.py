"""
Prompt Builder — Transforms DAG queries into structured LLM prompts.

Ensures repeatable and constrained reasoning by grounding the LLM
in the causal structure of the graph.
"""

from __future__ import annotations

from typing import Any

from app.core.dag_engine import CausalDAG


SYSTEM_PROMPT_TEMPLATE = """Je bent een causale redeneerassistent voor het domein sportdeelname.
Je redeneert UITSLUITEND op basis van het causale model dat je krijgt aangeleverd.
Je verzint geen nieuwe causale relaties. Je geeft aan als het model onvoldoende
informatie bevat om een vraag te beantwoorden.

Causaal model: {model_name} (versie {model_version})
Beschrijving: {model_description}

Regels:
1. Gebruik alleen de causale relaties uit het model
2. Geef bij elke conclusie aan welk causaal pad je volgt
3. Vermeld de sterkte en richting van elke relatie
4. Als een vraag buiten het model valt, zeg dit expliciet
5. Antwoord in het Nederlands
"""

QUERY_TEMPLATE = """Vraag van de gebruiker:
{user_query}

Relevante causale context uit het model:

{causal_context}

Beantwoord de vraag op basis van bovenstaande causale relaties.
Structureer je antwoord als volgt:
1. Samenvatting (1-2 zinnen)
2. Causale redenering (stap voor stap, verwijzend naar het model)
3. Beperkingen (wat het model niet kan vertellen)
"""

INTERVENTION_TEMPLATE = """De gebruiker wil weten wat er gebeurt als de volgende interventie plaatsvindt:

Interventie: {intervention_description}
Factor: {factor_label} ({factor_id})
Verandering: {change_description}

Geschatte effecten volgens het causale model:

{effects_description}

Geef een analyse van deze interventie:
1. Verwachte directe effecten
2. Verwachte indirecte effecten (via welke paden)
3. Mogelijke risico's of onbedoelde effecten
4. Aanbevelingen
"""


class PromptBuilder:
    """Builds structured LLM prompts from DAG queries."""

    def __init__(self, dag: CausalDAG):
        self.dag = dag

    def build_system_prompt(self) -> str:
        """Build the system prompt with model context."""
        return SYSTEM_PROMPT_TEMPLATE.format(
            model_name=self.dag.name,
            model_version=self.dag.version,
            model_description=self.dag.description,
        )

    def build_query_prompt(self, user_query: str, factor_ids: list[str] | None = None) -> str:
        """Build a query prompt with relevant causal context.

        Args:
            user_query: The user's natural language question.
            factor_ids: Optional list of factor IDs to focus on.
                        If None, tries to identify relevant factors.
        """
        context_parts = []

        if factor_ids:
            for fid in factor_ids:
                context_parts.append(self._describe_factor_context(fid))
        else:
            # Include full model overview for general queries
            context_parts.append(self._describe_full_model())

        causal_context = "\n\n".join(context_parts)

        return QUERY_TEMPLATE.format(
            user_query=user_query,
            causal_context=causal_context,
        )

    def build_intervention_prompt(
        self,
        factor_id: str,
        change: float,
        description: str = "",
    ) -> str:
        """Build a prompt for intervention analysis."""
        factor_info = self.dag.get_factor_info(factor_id)
        if not factor_info:
            raise ValueError(f"Factor '{factor_id}' not found in the model")

        effects = self.dag.simulate_intervention(factor_id, change)
        effects_desc = self._format_effects(effects)

        change_desc = f"{'toename' if change > 0 else 'afname'} van {abs(change) * 100:.0f}%"

        return INTERVENTION_TEMPLATE.format(
            intervention_description=description or f"Verandering in {factor_info['label']}",
            factor_label=factor_info["label"],
            factor_id=factor_id,
            change_description=change_desc,
            effects_description=effects_desc,
        )

    def build_full_prompt(
        self,
        user_query: str,
        factor_ids: list[str] | None = None,
    ) -> list[dict[str, str]]:
        """Build a complete prompt (system + user) ready for LLM API call."""
        return [
            {"role": "system", "content": self.build_system_prompt()},
            {"role": "user", "content": self.build_query_prompt(user_query, factor_ids)},
        ]

    def _describe_factor_context(self, factor_id: str) -> str:
        """Describe a factor and its immediate causal context."""
        info = self.dag.get_factor_info(factor_id)
        if not info:
            return f"Factor '{factor_id}' niet gevonden in het model."

        lines = [f"### Factor: {info['label']} ({factor_id})"]
        if info.get("description"):
            lines.append(f"Beschrijving: {info['description']}")

        if info["causes"]:
            lines.append("\nOorzaken (wat beïnvloedt deze factor):")
            for cause in info["causes"]:
                rel = cause["relation"]
                lines.append(
                    f"  - {cause['label']} → {info['label']}: "
                    f"{rel['direction']}, sterkte {rel['strength']}"
                )

        if info["effects"]:
            lines.append("\nEffecten (wat deze factor beïnvloedt):")
            for effect in info["effects"]:
                rel = effect["relation"]
                lines.append(
                    f"  - {info['label']} → {effect['label']}: "
                    f"{rel['direction']}, sterkte {rel['strength']}"
                )

        return "\n".join(lines)

    def _describe_full_model(self) -> str:
        """Describe the complete model overview."""
        summary = self.dag.get_graph_summary()
        factors = self.dag.get_all_factors()
        relations = self.dag.get_all_relations()

        lines = [
            f"### Model: {summary['name']} v{summary['version']}",
            f"Factoren: {summary['num_factors']}, Relaties: {summary['num_relations']}",
            "",
            "Factoren:",
        ]

        for f in factors:
            lines.append(f"  - {f['label']} ({f['id']}): {f.get('description', '')}")

        lines.append("\nCausale relaties:")
        for r in relations:
            cause_label = self.dag.graph.nodes[r["cause"]].get("label", r["cause"])
            effect_label = self.dag.graph.nodes[r["effect"]].get("label", r["effect"])
            lines.append(
                f"  - {cause_label} → {effect_label}: "
                f"{r['direction']}, sterkte {r['strength']}"
                + (f" ({r['description']})" if r.get("description") else "")
            )

        return "\n".join(lines)

    def _format_effects(self, effects: list[dict[str, Any]]) -> str:
        """Format intervention effects as readable text."""
        if not effects:
            return "Geen verwachte effecten gevonden in het model."

        lines = []
        for effect in effects:
            impact = effect["estimated_impact"]
            direction = "positief" if impact > 0 else "negatief"
            path = " → ".join(effect["path"])
            lines.append(
                f"  - {effect['label']}: {direction} effect ({impact:+.1%}), "
                f"via pad: {path}"
            )
        return "\n".join(lines)
