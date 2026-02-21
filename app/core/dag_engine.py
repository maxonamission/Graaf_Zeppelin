"""
DAG Engine — Graph-based causal reasoning engine.

Uses NetworkX to represent and query directed acyclic graphs (DAGs)
for causal inference in the sports participation domain.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx


class CausalDAG:
    """A directed acyclic graph representing causal relationships."""

    def __init__(self, name: str, version: str, description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.graph = nx.DiGraph()

    def add_factor(
        self,
        factor_id: str,
        label: str,
        description: str = "",
        category: str = "",
        **attrs: Any,
    ) -> None:
        """Add a causal factor (node) to the graph."""
        self.graph.add_node(
            factor_id,
            label=label,
            description=description,
            category=category,
            **attrs,
        )

    def add_relation(
        self,
        cause: str,
        effect: str,
        direction: str = "positive",
        strength: float = 0.5,
        description: str = "",
        **attrs: Any,
    ) -> None:
        """Add a causal relation (edge) between two factors.

        Args:
            cause: Source factor ID.
            effect: Target factor ID.
            direction: 'positive' or 'negative'.
            strength: 0.0 (weak) to 1.0 (strong).
            description: Human-readable description of the relation.
        """
        if cause not in self.graph:
            raise ValueError(f"Factor '{cause}' does not exist in the graph")
        if effect not in self.graph:
            raise ValueError(f"Factor '{effect}' does not exist in the graph")
        if not 0.0 <= strength <= 1.0:
            raise ValueError("Strength must be between 0.0 and 1.0")

        self.graph.add_edge(
            cause,
            effect,
            direction=direction,
            strength=strength,
            description=description,
            **attrs,
        )

        # Validate DAG property (no cycles)
        if not nx.is_directed_acyclic_graph(self.graph):
            self.graph.remove_edge(cause, effect)
            raise ValueError(
                f"Adding relation {cause} → {effect} would create a cycle"
            )

    def get_causes(self, factor_id: str) -> list[dict[str, Any]]:
        """Get all direct causes (parents) of a factor."""
        causes = []
        for pred in self.graph.predecessors(factor_id):
            edge_data = self.graph.edges[pred, factor_id]
            causes.append(
                {
                    "factor": pred,
                    **self.graph.nodes[pred],
                    "relation": edge_data,
                }
            )
        return causes

    def get_effects(self, factor_id: str) -> list[dict[str, Any]]:
        """Get all direct effects (children) of a factor."""
        effects = []
        for succ in self.graph.successors(factor_id):
            edge_data = self.graph.edges[factor_id, succ]
            effects.append(
                {
                    "factor": succ,
                    **self.graph.nodes[succ],
                    "relation": edge_data,
                }
            )
        return effects

    def get_causal_paths(
        self, source: str, target: str
    ) -> list[list[str]]:
        """Find all causal paths from source to target."""
        try:
            return list(nx.all_simple_paths(self.graph, source, target))
        except nx.NetworkXError:
            return []

    def get_ancestors(self, factor_id: str) -> set[str]:
        """Get all upstream factors (transitive causes)."""
        return nx.ancestors(self.graph, factor_id)

    def get_descendants(self, factor_id: str) -> set[str]:
        """Get all downstream factors (transitive effects)."""
        return nx.descendants(self.graph, factor_id)

    def simulate_intervention(
        self, factor_id: str, change: float
    ) -> list[dict[str, Any]]:
        """Simulate what happens when a factor changes.

        Returns a list of affected factors with estimated impact,
        propagated through the causal graph.
        """
        affected = []
        visited = set()

        def propagate(current: str, current_impact: float, path: list[str]) -> None:
            for successor in self.graph.successors(current):
                if successor in visited:
                    continue
                visited.add(successor)

                edge = self.graph.edges[current, successor]
                strength = edge["strength"]
                direction_multiplier = 1.0 if edge["direction"] == "positive" else -1.0
                impact = current_impact * strength * direction_multiplier

                new_path = path + [successor]
                affected.append(
                    {
                        "factor": successor,
                        **self.graph.nodes[successor],
                        "estimated_impact": round(impact, 3),
                        "path": new_path,
                    }
                )
                propagate(successor, impact, new_path)

        visited.add(factor_id)
        propagate(factor_id, change, [factor_id])

        # Sort by absolute impact (most affected first)
        affected.sort(key=lambda x: abs(x["estimated_impact"]), reverse=True)
        return affected

    def get_factor_info(self, factor_id: str) -> dict[str, Any] | None:
        """Get full information about a factor."""
        if factor_id not in self.graph:
            return None
        return {
            "id": factor_id,
            **self.graph.nodes[factor_id],
            "causes": self.get_causes(factor_id),
            "effects": self.get_effects(factor_id),
            "ancestors": list(self.get_ancestors(factor_id)),
            "descendants": list(self.get_descendants(factor_id)),
        }

    def get_all_factors(self) -> list[dict[str, Any]]:
        """Get all factors with their basic attributes."""
        return [
            {"id": node, **self.graph.nodes[node]}
            for node in self.graph.nodes
        ]

    def get_all_relations(self) -> list[dict[str, Any]]:
        """Get all causal relations."""
        return [
            {"cause": u, "effect": v, **data}
            for u, v, data in self.graph.edges(data=True)
        ]

    def get_graph_summary(self) -> dict[str, Any]:
        """Get summary statistics of the graph."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "num_factors": self.graph.number_of_nodes(),
            "num_relations": self.graph.number_of_edges(),
            "root_factors": [
                n for n in self.graph.nodes if self.graph.in_degree(n) == 0
            ],
            "leaf_factors": [
                n for n in self.graph.nodes if self.graph.out_degree(n) == 0
            ],
        }

    def to_dict(self) -> dict[str, Any]:
        """Serialize the graph to a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "factors": [
                {"id": n, **self.graph.nodes[n]} for n in self.graph.nodes
            ],
            "relations": [
                {"cause": u, "effect": v, **d}
                for u, v, d in self.graph.edges(data=True)
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CausalDAG:
        """Deserialize a graph from a dictionary."""
        dag = cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
        )
        for factor in data["factors"]:
            factor_id = factor.pop("id")
            dag.add_factor(factor_id, **factor)

        for relation in data["relations"]:
            cause = relation.pop("cause")
            effect = relation.pop("effect")
            dag.add_relation(cause, effect, **relation)

        return dag

    def save(self, path: str | Path) -> None:
        """Save the graph to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str | Path) -> CausalDAG:
        """Load a graph from a JSON file."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
