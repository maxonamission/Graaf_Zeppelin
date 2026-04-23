"""
DAG Engine — Graph-based causal reasoning engine.

Uses NetworkX to represent and query directed acyclic graphs (DAGs)
for causal inference in the sports participation domain.

Supports both v1 schema (factors/relations) and v2 schema
(nodes/edges with domains, moderators, sliders).
"""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import networkx as nx

# Edge-types whose collective subgraph must remain acyclic. FEEDBACK and
# SOCIAL_REGULATORY edges are semantically cyclic (feedback loops, social
# regulation) and are excluded from the acyclicity constraint — see
# stories/done/S14-01-cycle-check-per-edge-type.md.
ACYCLIC_EDGE_TYPES: frozenset[str] = frozenset(
    {"STRUCTURAL", "MEDIATING", "MODERATOR"}
)

# Mapping from v2 polarity strings to v1 direction strings (NL + EN — S12-05)
_POLARITY_MAP = {
    "positief": "positive",
    "negatief": "negative",
    "variabel": "variable",
    "positive": "positive",
    "negative": "negative",
    "variable": "variable",
}

# Mapping from v2 strength labels to numeric fallback (NL + EN — S12-05)
_STRENGTH_MAP = {
    "sterk": 0.8,
    "midden": 0.5,
    "zwak": 0.2,
    "strong": 0.8,
    "medium": 0.5,
    "weak": 0.2,
}


def _acyclic_subgraph(graph: nx.DiGraph) -> nx.DiGraph:
    """Return the subgraph induced by edges whose edge_type is acyclic.

    Edges without an ``edge_type`` attribute are treated as acyclic-constrained
    (this preserves v1-schema behaviour, where the concept does not exist).
    """
    sub: nx.DiGraph = nx.DiGraph()
    sub.add_nodes_from(graph.nodes(data=True))
    for u, v, data in graph.edges(data=True):
        edge_type = data.get("edge_type")
        if edge_type is None or edge_type in ACYCLIC_EDGE_TYPES:
            sub.add_edge(u, v, **data)
    return sub


def _assert_acyclic(graph: nx.DiGraph) -> None:
    """Raise ValueError if the acyclic subgraph contains a cycle.

    The error message names the edges in the offending cycle and their
    ``edge_type`` values, to make debugging quick.
    """
    sub = _acyclic_subgraph(graph)
    if nx.is_directed_acyclic_graph(sub):
        return
    cycles = list(nx.simple_cycles(sub))
    if not cycles:
        return
    first = cycles[0]
    pieces = []
    for i, u in enumerate(first):
        v = first[(i + 1) % len(first)]
        etype = sub.edges[u, v].get("edge_type", "<no edge_type>")
        pieces.append(f"{u}→{v} [{etype}]")
    raise ValueError(
        "Cycle detected among acyclic edge types "
        f"{sorted(ACYCLIC_EDGE_TYPES)}: " + " → ".join(pieces)
    )


class CausalDAG:
    """A directed graph representing causal relationships.

    Despite the name, v2 models may contain feedback loops and are
    therefore general directed graphs rather than strict DAGs.
    """

    def __init__(self, name: str, version: str, description: str = ""):
        self.name = name
        self.version = version
        self.description = description
        self.graph = nx.DiGraph()
        self.moderators: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.sliders: list[dict[str, Any]] = []
        self.metadata: dict[str, Any] = {}
        self._schema_version: int = 1

    # ── Model metadata properties (S12-06) ─────────────────────────────

    @property
    def domain_name(self) -> str:
        """Domain display name from metadata, fallback to project name."""
        return self.metadata.get("domain_name", self.name)

    @property
    def example_questions(self) -> dict[str, list[str]]:
        """Example questions per context (reasoning/wizard), or empty arrays."""
        eq = self.metadata.get("example_questions", {})
        return {
            "reasoning": eq.get("reasoning", []),
            "wizard": eq.get("wizard", []),
        }

    @property
    def persona(self) -> str:
        """AI persona from metadata, or generic fallback."""
        return self.metadata.get("persona", "beleidsadviseur")

    @property
    def language(self) -> str:
        """Language code from metadata, default 'nl'."""
        return self.metadata.get("language", "nl")

    # ── Node operations ──────────────────────────────────────────────────

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

    # ── Edge operations ──────────────────────────────────────────────────

    def add_relation(
        self,
        cause: str,
        effect: str,
        direction: str = "positive",
        strength: float = 0.5,
        description: str = "",
        *,
        check_dag: bool = True,
        **attrs: Any,
    ) -> None:
        """Add a causal relation (edge) between two factors.

        Args:
            cause: Source factor ID.
            effect: Target factor ID.
            direction: 'positive' or 'negative'.
            strength: 0.0 (weak) to 1.0 (strong).
            description: Human-readable description of the relation.
            check_dag: If True, validate that the graph remains acyclic.
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

        # Validate acyclicity on the subgraph of acyclic edge-types only.
        # Edges without an edge_type (v1 schema) are treated as acyclic-constrained.
        if check_dag:
            try:
                _assert_acyclic(self.graph)
            except ValueError as exc:
                self.graph.remove_edge(cause, effect)
                raise ValueError(
                    f"Adding relation {cause} → {effect} would create a cycle: "
                    f"{exc}"
                ) from None

    def add_moderator(
        self,
        edge_id: str,
        moderator_node: str,
        **attrs: Any,
    ) -> None:
        """Register a moderator relationship (node → edge)."""
        self.moderators[edge_id].append({
            "moderator_node": moderator_node,
            **attrs,
        })

    # ── Query: nodes ─────────────────────────────────────────────────────

    def get_causes(self, factor_id: str) -> list[dict[str, Any]]:
        """Get all direct causes (parents) of a factor."""
        causes = []
        for pred in self.graph.predecessors(factor_id):
            edge_data = dict(self.graph.edges[pred, factor_id])
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
            edge_data = dict(self.graph.edges[factor_id, succ])
            effects.append(
                {
                    "factor": succ,
                    **self.graph.nodes[succ],
                    "relation": edge_data,
                }
            )
        return effects

    def get_causal_paths(
        self, source: str, target: str, max_length: int = 5
    ) -> list[list[str]]:
        """Find all causal paths from source to target."""
        try:
            return list(
                nx.all_simple_paths(self.graph, source, target, cutoff=max_length)
            )
        except nx.NetworkXError:
            return []

    def get_ancestors(self, factor_id: str) -> set[str]:
        """Get all upstream factors (transitive causes)."""
        return nx.ancestors(self.graph, factor_id)

    def get_descendants(self, factor_id: str) -> set[str]:
        """Get all downstream factors (transitive effects)."""
        return nx.descendants(self.graph, factor_id)

    def get_factor_info(self, factor_id: str) -> dict[str, Any] | None:
        """Get full information about a factor including moderators."""
        if factor_id not in self.graph:
            return None

        info = {
            "id": factor_id,
            **self.graph.nodes[factor_id],
            "causes": self.get_causes(factor_id),
            "effects": self.get_effects(factor_id),
            "ancestors": list(self.get_ancestors(factor_id)),
            "descendants": list(self.get_descendants(factor_id)),
        }

        # Add moderator info for edges connected to this node
        if self._schema_version >= 2:
            moderated_edges = []
            for edge_id, mods in self.moderators.items():
                for mod in mods:
                    if mod["moderator_node"] == factor_id:
                        moderated_edges.append({
                            "edge_id": edge_id,
                            **mod,
                        })
            if moderated_edges:
                info["moderates_edges"] = moderated_edges

        return info

    def get_all_factors(
        self,
        domain: str | None = None,
        cluster: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all factors with optional filtering."""
        factors = []
        for node in self.graph.nodes:
            attrs = self.graph.nodes[node]
            if domain and attrs.get("domain") != domain:
                continue
            if cluster and attrs.get("cluster") != cluster:
                continue
            if status and attrs.get("status") != status:
                continue
            factors.append({"id": node, **attrs})
        return factors

    def get_all_relations(
        self,
        cluster: str | None = None,
        polarity: str | None = None,
        edge_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get all causal relations with optional filtering."""
        relations = []
        for u, v, data in self.graph.edges(data=True):
            if cluster and data.get("cluster") != cluster:
                continue
            if polarity and data.get("direction") != polarity:
                continue
            if edge_type and data.get("edge_type") != edge_type:
                continue
            relations.append({"cause": u, "effect": v, **data})
        return relations

    # ── Query: domains ───────────────────────────────────────────────────

    def get_domains(self) -> dict[str, int]:
        """Get domain names with node counts."""
        domains: dict[str, int] = defaultdict(int)
        for node in self.graph.nodes:
            domain = self.graph.nodes[node].get("domain", "")
            if domain:
                domains[domain] += 1
        return dict(sorted(domains.items()))

    def get_nodes_by_domain(self, domain: str) -> list[dict[str, Any]]:
        """Get all nodes in a specific domain."""
        return self.get_all_factors(domain=domain)

    # ── Query: sliders ───────────────────────────────────────────────────

    def get_sliders(self) -> list[dict[str, Any]]:
        """Get all slider definitions."""
        return list(self.sliders)

    def get_slider(self, slider_id: str) -> dict[str, Any] | None:
        """Get a single slider by ID."""
        for s in self.sliders:
            if s.get("id") == slider_id:
                return s
        return None

    def get_slider_qualifiers(self, slider_id: str) -> list[dict[str, Any]] | None:
        """Get qualifying questions for a specific slider."""
        slider = self.get_slider(slider_id)
        if not slider:
            return None
        return slider.get("qualifiers", [])

    def get_relevant_sliders(self, factor_ids: list[str]) -> list[dict[str, Any]]:
        """Find sliders that are relevant for the given factors.

        A slider is relevant if any of the given factor IDs appears in the
        slider's related_nodes, or if the factor belongs to a cluster that
        the slider primarily affects.
        """
        if not factor_ids:
            return list(self.sliders)

        # Collect clusters for the given factors
        factor_clusters: set[str] = set()
        for fid in factor_ids:
            node = self.graph.nodes.get(fid)
            if node:
                cluster = node.get("cluster", "")
                if cluster:
                    factor_clusters.add(cluster)

        relevant = []
        for slider in self.sliders:
            related_nodes = set(slider.get("related_nodes", []))
            primary_clusters = set(slider.get("primary_clusters", []))

            # Check direct node overlap
            if related_nodes & set(factor_ids):
                relevant.append(slider)
                continue

            # Check cluster overlap
            if primary_clusters & factor_clusters:
                relevant.append(slider)

        return relevant

    # ── Query: moderators ────────────────────────────────────────────────

    def get_edge_moderators(self, edge_id: str) -> list[dict[str, Any]]:
        """Get all moderators for a specific edge."""
        return list(self.moderators.get(edge_id, []))

    # ── Simulation ───────────────────────────────────────────────────────

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
                direction = edge.get("direction", "positive")
                if direction == "positive":
                    direction_multiplier = 1.0
                elif direction == "negative":
                    direction_multiplier = -1.0
                else:
                    direction_multiplier = 1.0  # variable/unknown
                impact = current_impact * strength * direction_multiplier

                new_path = path + [successor]
                affected.append(
                    {
                        "factor": successor,
                        **self.graph.nodes[successor],
                        "estimated_impact": round(impact, 3),
                        "path": new_path,
                        "mechanism": edge.get("mechanism", ""),
                    }
                )
                propagate(successor, impact, new_path)

        visited.add(factor_id)
        propagate(factor_id, change, [factor_id])

        # Sort by absolute impact (most affected first)
        affected.sort(key=lambda x: abs(x["estimated_impact"]), reverse=True)
        return affected

    # ── Factor search ─────────────────────────────────────────────────────

    def find_relevant_factors(
        self, query: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        """Find factors relevant to a natural-language query.

        Uses keyword matching against factor labels, definitions, and domains.
        Returns factors sorted by relevance (number of keyword matches).
        """
        # Normalize and split query into searchable terms (>= 3 chars)
        query_lower = query.lower()
        terms = [t for t in query_lower.split() if len(t) >= 3]
        if not terms:
            return []

        scored: list[tuple[int, str, dict[str, Any]]] = []
        for node_id in self.graph.nodes:
            attrs = self.graph.nodes[node_id]
            # S12-01: dynamically search all string-valued attributes
            searchable = " ".join(
                str(v) for v in attrs.values() if isinstance(v, str)
            ).lower()

            score = sum(1 for t in terms if t in searchable)
            if score > 0:
                scored.append((score, node_id, attrs))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"id": node_id, **attrs}
            for _, node_id, attrs in scored[:max_results]
        ]

    # ── Response validation ───────────────────────────────────────────────

    def validate_response_factors(self, response_text: str) -> dict[str, Any]:
        """Check which factor labels from the model appear in an LLM response.

        Returns a dict with recognized and unrecognized factor references,
        helping detect potential hallucinations.
        """
        text_lower = response_text.lower()
        recognized = []
        for node_id in self.graph.nodes:
            label = self.graph.nodes[node_id].get("label", "")
            if label and label.lower() in text_lower:
                recognized.append({
                    "id": node_id,
                    "label": label,
                    "domain": self.graph.nodes[node_id].get("domain", ""),
                })
        return {
            "recognized_factors": recognized,
            "recognized_count": len(recognized),
            "model_factor_count": self.graph.number_of_nodes(),
        }

    # ── Summary ──────────────────────────────────────────────────────────

    def get_graph_summary(self) -> dict[str, Any]:
        """Get summary statistics of the graph."""
        summary: dict[str, Any] = {
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

        if self._schema_version >= 2:
            summary["domains"] = self.get_domains()
            summary["num_sliders"] = len(self.sliders)
            summary["num_moderators"] = sum(
                len(mods) for mods in self.moderators.values()
            )
            if self.metadata.get("graph_metrics"):
                summary["graph_metrics"] = self.metadata["graph_metrics"]

        return summary

    # ── Serialization ────────────────────────────────────────────────────

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
        """Deserialize a graph from a dictionary. Auto-detects v1 vs v2 schema."""
        is_v2 = "nodes" in data and "edges" in data

        if is_v2:
            return cls._from_dict_v2(data)
        return cls._from_dict_v1(data)

    @classmethod
    def _from_dict_v1(cls, data: dict[str, Any]) -> CausalDAG:
        """Load v1 schema (factors/relations)."""
        dag = cls(
            name=data["name"],
            version=data["version"],
            description=data.get("description", ""),
        )
        dag._schema_version = 1

        for factor in data["factors"]:
            factor = dict(factor)  # don't mutate original
            factor_id = factor.pop("id")
            dag.add_factor(factor_id, **factor)

        for relation in data["relations"]:
            relation = dict(relation)
            cause = relation.pop("cause")
            effect = relation.pop("effect")
            dag.add_relation(cause, effect, **relation)

        return dag

    @classmethod
    def _from_dict_v2(cls, data: dict[str, Any]) -> CausalDAG:
        """Load v2 schema (nodes/edges/sliders with domains, moderators, etc.)."""
        meta = data.get("metadata", {})
        summary = meta.get("summary", {})

        dag = cls(
            name=meta.get("project", data.get("name", "Unknown")),
            version=meta.get("version", "0.0.0"),
            description=summary.get("description", ""),
        )
        dag._schema_version = 2
        dag.metadata = meta

        # Load nodes — S12-01: accept all fields dynamically
        for node in data["nodes"]:
            node = dict(node)  # don't mutate original
            node_id = node.pop("id")
            # Ensure common fields exist for backward compat
            node.setdefault("label", "")
            node.setdefault("description", node.get("definition", ""))
            node.setdefault("definition", node.get("description", ""))
            node.setdefault("domain", "")
            node.setdefault("category", node.get("domain", ""))
            # All remaining fields are added as-is (extra_attrs)
            dag.graph.add_node(node_id, **node)

        # Load edges — S12-01: dynamic field parsing
        for edge in data["edges"]:
            edge = dict(edge)  # don't mutate original
            target_type = edge.get("target_type", "node")

            if target_type == "edge":
                # Moderator edge: store separately
                dag.moderators[edge["target"]].append({
                    "id": edge.get("id", ""),
                    "moderator_node": edge["source"],
                    "moderator_label": edge.get("source_label", ""),
                    "target_edge": edge["target"],
                    "target_label": edge.get("target_label", ""),
                    "mechanism": edge.get("mechanism", ""),
                    "strength": _STRENGTH_MAP.get(
                        edge.get("strength", ""), edge.get("base_weight", 0.5)
                    ),
                    "polarity": edge.get("polarity", ""),
                    "literature": edge.get("literature", []),
                })
                continue

            source = edge.pop("source")
            target = edge.pop("target")
            edge.pop("target_type", None)

            if source not in dag.graph or target not in dag.graph:
                continue

            # Map polarity to direction for backward compat (S12-05: NL+EN)
            polarity = edge.get("polarity", "positief")
            direction = _POLARITY_MAP.get(polarity, "positive")  # graceful fallback

            # Use base_weight as numeric strength, fall back to label mapping
            strength = edge.get("base_weight", _STRENGTH_MAP.get(
                edge.get("strength", ""), 0.5  # graceful fallback
            ))

            # Set computed fields, keep all original fields as-is
            edge["direction"] = direction
            edge["strength"] = strength
            edge.setdefault("description", edge.get("mechanism", ""))
            edge.setdefault("mechanism", edge.get("description", ""))

            dag.graph.add_edge(source, target, **edge)

        # Load sliders
        dag.sliders = data.get("sliders", [])

        # Enforce acyclicity on the subgraph of acyclic edge-types.
        # FEEDBACK and SOCIAL_REGULATORY edges may form cycles by design.
        _assert_acyclic(dag.graph)

        return dag

    def save(self, path: str | Path) -> None:
        """Save the graph to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: str | Path) -> CausalDAG:
        """Load a graph from a JSON file. Auto-detects v1/v2 schema."""
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
