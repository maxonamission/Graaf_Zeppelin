"""Graph-level invariants catalog — S14-04.

Collection-level checks (cycles, orphans, duplicate IDs, dangling edge
references, connectivity, edge-value ranges) bundled into a single
``ValidationReport``. Per-edge and per-node value validation (enum
membership, numeric ranges of individual fields) is partly duplicated
here but will be owned by Pydantic models once S14-02 lands — keep this
module focused on graph-level invariants.

Standard usage:

    from app.core.validation import validate
    import json

    with open("data/models/sportdeelname_graph.json") as f:
        data = json.load(f)
    report = validate(data)
    print(report.summary())
    if not report.is_valid:
        raise SystemExit(1)

See ``scripts/validate_graph.py`` for the CLI wrapper.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

import networkx as nx

from app.core.dag_engine import (
    ACYCLIC_EDGE_TYPES,
    CausalDAG,
    _acyclic_subgraph,
)

# Strength values the loader accepts (NL + EN, plus the empty string used
# in some v2 edges where base_weight is the primary source of truth).
_VALID_STRENGTH_ENUM: frozenset[str] = frozenset(
    {"sterk", "midden", "zwak", "strong", "medium", "weak", ""}
)


@dataclass
class ValidationReport:
    """Aggregated result of all graph-level invariant checks.

    ``is_valid`` is True iff ``errors`` is empty. ``warnings`` never block
    validity (e.g. orphan nodes are often intentional during incremental
    model development).
    """

    is_valid: bool = True
    node_count: int = 0
    edge_count: int = 0
    cycles: list[list[str]] = field(default_factory=list)
    orphan_nodes: list[str] = field(default_factory=list)
    duplicate_node_ids: list[str] = field(default_factory=list)
    duplicate_edge_ids: list[str] = field(default_factory=list)
    dangling_refs: list[dict[str, str]] = field(default_factory=list)
    weakly_connected_components: int = 0
    edge_weight_violations: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        """Human-readable summary, one line per category."""
        status = "OK" if self.is_valid else "INVALID"
        lines = [
            f"ValidationReport: {status}",
            f"  nodes:                         {self.node_count}",
            f"  edges:                         {self.edge_count}",
            f"  weakly-connected components:   {self.weakly_connected_components}",
            f"  cycles (acyclic subgraph):     {len(self.cycles)}",
            f"  orphan nodes:                  {len(self.orphan_nodes)}",
            f"  duplicate node IDs:            {len(self.duplicate_node_ids)}",
            f"  duplicate edge IDs:            {len(self.duplicate_edge_ids)}",
            f"  dangling refs:                 {len(self.dangling_refs)}",
            f"  edge-weight violations:        {len(self.edge_weight_violations)}",
            f"  warnings:                      {len(self.warnings)}",
            f"  errors:                        {len(self.errors)}",
        ]
        if self.errors:
            lines.append("errors:")
            lines.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            lines.append("warnings:")
            lines.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(lines)


# ── Individual checks ────────────────────────────────────────────────


def detect_cycles(
    graph: nx.DiGraph,
    *,
    acyclic_edge_types: frozenset[str] = ACYCLIC_EDGE_TYPES,
) -> list[list[str]]:
    """Enumerate cycles that violate the acyclicity constraint.

    Only edges whose ``edge_type`` is in ``acyclic_edge_types`` are
    considered. Edges without an ``edge_type`` attribute are treated as
    acyclic-constrained (v1-schema behaviour).
    """
    if acyclic_edge_types == ACYCLIC_EDGE_TYPES:
        sub = _acyclic_subgraph(graph)
    else:
        sub = nx.DiGraph()
        sub.add_nodes_from(graph.nodes(data=True))
        for u, v, data in graph.edges(data=True):
            edge_type = data.get("edge_type")
            if edge_type is None or edge_type in acyclic_edge_types:
                sub.add_edge(u, v, **data)
    return [list(cycle) for cycle in nx.simple_cycles(sub)]


def find_orphan_nodes(
    graph: nx.DiGraph,
    *,
    extra_participating_ids: frozenset[str] = frozenset(),
) -> list[str]:
    """Nodes without any edges (in or out) in the directed graph.

    ``extra_participating_ids`` lets callers exclude nodes that participate
    in the model through channels not represented as NetworkX edges — most
    notably moderator edges, which the loader stores in
    ``CausalDAG.moderators`` instead of on the graph itself. A node that
    only appears as a moderator source would otherwise be flagged as
    orphan incorrectly.
    """
    return sorted(
        n
        for n in graph.nodes
        if graph.in_degree(n) == 0
        and graph.out_degree(n) == 0
        and n not in extra_participating_ids
    )


def find_duplicate_ids(raw_data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (duplicate_node_ids, duplicate_edge_ids) from raw JSON.

    NetworkX silently deduplicates nodes on ``add_node`` with a duplicate
    id, so this check must run on the raw JSON before loading.
    """
    nodes = raw_data.get("nodes", raw_data.get("factors", []))
    edges = raw_data.get("edges", raw_data.get("relations", []))

    def _dupes(ids: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for i in ids:
            if i is None:
                continue
            if i in seen and i not in out:
                out.append(i)
            seen.add(i)
        return out

    node_ids = [n.get("id") for n in nodes]
    edge_ids = [e.get("id") for e in edges if e.get("id") is not None]
    return _dupes(node_ids), _dupes(edge_ids)


def find_dangling_refs(raw_data: dict[str, Any]) -> list[dict[str, str]]:
    """Edges whose source/target refers to an unknown node id.

    Moderator edges (``target_type == "edge"``) target another edge, not a
    node, and are excluded from this check.
    """
    nodes = raw_data.get("nodes", raw_data.get("factors", []))
    edges = raw_data.get("edges", raw_data.get("relations", []))

    node_ids = {n.get("id") for n in nodes if n.get("id") is not None}
    # Also collect edge ids, so moderator target references can be sanity-checked
    edge_ids = {e.get("id") for e in edges if e.get("id") is not None}

    dangling: list[dict[str, str]] = []
    for e in edges:
        edge_id = e.get("id", "<no-id>")
        source = e.get("source", e.get("cause"))
        target = e.get("target", e.get("effect"))
        target_type = e.get("target_type", "node")

        if source is not None and source not in node_ids:
            dangling.append(
                {"edge_id": edge_id, "field": "source", "invalid_id": source}
            )

        if target is None:
            continue
        if target_type == "edge":
            # Moderator: target must be an existing edge id
            if target not in edge_ids:
                dangling.append(
                    {"edge_id": edge_id, "field": "target(edge)", "invalid_id": target}
                )
        elif target not in node_ids:
            dangling.append(
                {"edge_id": edge_id, "field": "target", "invalid_id": target}
            )
    return dangling


def check_connectivity(graph: nx.DiGraph) -> int:
    """Number of weakly connected components (0 for an empty graph)."""
    if graph.number_of_nodes() == 0:
        return 0
    return nx.number_weakly_connected_components(graph)


def validate_edge_weights(graph: nx.DiGraph) -> list[dict[str, Any]]:
    """Per-edge range/enum checks on ``base_weight`` and ``strength``.

    ``base_weight`` must be in [0.0, 1.0] when present. ``strength`` must
    be either numeric or a known enum value (NL + EN). The loader already
    coerces ``strength`` to a float for the NetworkX edge attribute, so we
    only flag values that neither are numeric nor recognised strings.
    """
    violations: list[dict[str, Any]] = []
    for u, v, data in graph.edges(data=True):
        edge_id = data.get("id", f"{u}->{v}")

        bw = data.get("base_weight")
        if bw is not None and isinstance(bw, (int, float)):
            if not (0.0 <= bw <= 1.0):
                violations.append(
                    {
                        "edge_id": edge_id,
                        "field": "base_weight",
                        "value": bw,
                        "reason": "must be in [0.0, 1.0]",
                    }
                )

        strength = data.get("strength")
        if isinstance(strength, str) and strength not in _VALID_STRENGTH_ENUM:
            violations.append(
                {
                    "edge_id": edge_id,
                    "field": "strength",
                    "value": strength,
                    "reason": (
                        "not numeric and not in enum "
                        f"{sorted(_VALID_STRENGTH_ENUM - {''})}"
                    ),
                }
            )
    return violations


# ── Orchestrator ─────────────────────────────────────────────────────


def validate_graph(raw_data: dict[str, Any]) -> ValidationReport:
    """Run all invariant checks and return an aggregated report.

    Does NOT raise on violations — the report accumulates errors so a
    caller (CLI, CI, loader integration) can react to all of them at
    once. Raises only on malformed input that cannot be parsed at all.
    """
    report = ValidationReport()

    # 1. Raw-JSON checks (before NetworkX dedup would hide them)
    node_dupes, edge_dupes = find_duplicate_ids(raw_data)
    report.duplicate_node_ids = node_dupes
    report.duplicate_edge_ids = edge_dupes
    if node_dupes:
        preview = ", ".join(node_dupes[:5])
        suffix = ", ..." if len(node_dupes) > 5 else ""
        report.errors.append(
            f"{len(node_dupes)} duplicate node ID(s): {preview}{suffix}"
        )
    if edge_dupes:
        preview = ", ".join(edge_dupes[:5])
        suffix = ", ..." if len(edge_dupes) > 5 else ""
        report.errors.append(
            f"{len(edge_dupes)} duplicate edge ID(s): {preview}{suffix}"
        )

    report.dangling_refs = find_dangling_refs(raw_data)
    if report.dangling_refs:
        first = report.dangling_refs[0]
        report.errors.append(
            f"{len(report.dangling_refs)} dangling edge reference(s); "
            f"first: edge {first['edge_id']} {first['field']}={first['invalid_id']}"
        )

    # 2. Build the graph (bypass strict acyclic assert — we report all findings)
    try:
        dag = CausalDAG.from_dict(raw_data, strict=False)
    except Exception as exc:  # pragma: no cover — defensive catch-all
        report.errors.append(f"Failed to load graph: {exc}")
        report.is_valid = False
        return report

    g = dag.graph
    report.node_count = g.number_of_nodes()
    report.edge_count = g.number_of_edges()
    report.weakly_connected_components = check_connectivity(g)

    # 3. Graph-level checks
    report.cycles = detect_cycles(g)
    if report.cycles:
        first = report.cycles[0]
        report.errors.append(
            f"{len(report.cycles)} cycle(s) in acyclic subgraph; "
            f"first: {' → '.join(first)} → {first[0]}"
        )

    # Moderator sources participate in the model even though their edges
    # live outside the NetworkX graph; exclude them from the orphan check.
    moderator_sources: frozenset[str] = frozenset(
        mod["moderator_node"]
        for mods in dag.moderators.values()
        for mod in mods
        if mod.get("moderator_node")
    )
    report.orphan_nodes = find_orphan_nodes(
        g, extra_participating_ids=moderator_sources
    )
    if report.orphan_nodes:
        preview = ", ".join(report.orphan_nodes[:5])
        suffix = ", ..." if len(report.orphan_nodes) > 5 else ""
        report.warnings.append(
            f"{len(report.orphan_nodes)} orphan node(s): {preview}{suffix}"
        )

    report.edge_weight_violations = validate_edge_weights(g)
    if report.edge_weight_violations:
        report.errors.append(
            f"{len(report.edge_weight_violations)} edge-weight violation(s)"
        )

    if report.weakly_connected_components > 1:
        report.warnings.append(
            f"Graph has {report.weakly_connected_components} weakly-connected "
            "components (disconnected pieces)"
        )

    report.is_valid = not report.errors
    return report
