"""Pydantic models for the causal graph — S14-02.

Canonical in-memory representation of the v2 graph schema used by Graaf
Zeppelin. Runtime validation catches ill-typed or inconsistent data at
load time (as a single ``ValidationError`` rather than a KeyError far
downstream).

Scope note — generic vs. project-specific taxonomy:
    Graph-level fields (id, source/target, polarity, strength,
    base_weight, edge_type) are grouped together under a ``Generic``
    comment; project-specific fields (bond_influence, slider_sensitivity,
    disciplines, cluster) follow under ``Project-specific``. The goal is
    to make a later formal split — anchored in the cross-project
    taxonomy wish in ``docs/uniforme-kenmerken-taxonomie.md`` — a simple
    mechanical refactor rather than a rethink of the whole model.

This module is schema-authoring only: it produces typed instances from
dicts and back, but does not build the NetworkX representation. That
still lives in ``app.core.dag_engine`` (``CausalDAG._from_dict_v2``),
which calls ``Graph.model_validate`` at the top of the strict load path.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ── Enums (values match data/models/sportdeelname_graph.json) ────────


class Polarity(StrEnum):
    POSITIEF = "positief"
    NEGATIEF = "negatief"
    VARIABEL = "variabel"
    MODERATOR = "moderator"


class Strength(StrEnum):
    STERK = "sterk"
    MIDDEN = "midden"
    ZWAK = "zwak"


class EdgeType(StrEnum):
    STRUCTURAL = "STRUCTURAL"
    MEDIATING = "MEDIATING"
    MODERATOR = "MODERATOR"
    FEEDBACK = "FEEDBACK"
    SOCIAL_REGULATORY = "SOCIAL_REGULATORY"


class CurveType(StrEnum):
    LINEAR = "LINEAR"
    INVERTED_U = "INVERTED_U"
    THRESHOLD_LOGISTIC = "THRESHOLD_LOGISTIC"


class TimeLag(StrEnum):
    """Retained for compatibility with the current v2 schema.

    S14-03 (Pad B) will remove ``time_lag`` from the schema and this
    enum. Until then we carry it as an Optional field so existing data
    loads cleanly.
    """

    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class BondInfluence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class NodeStatus(StrEnum):
    """Validation level from the model-curation process."""

    A = "A"
    B = "B"
    DASH = "-"


class TargetType(StrEnum):
    """Whether an edge targets a node or another edge (moderator)."""

    NODE = "node"
    EDGE = "edge"


# EN→NL aliases accepted on input (S12-05 meertaligheid).
_POLARITY_ALIASES: dict[str, str] = {
    "positive": "positief",
    "negative": "negatief",
    "variable": "variabel",
}
_STRENGTH_ALIASES: dict[str, str] = {
    "strong": "sterk",
    "medium": "midden",
    "weak": "zwak",
}


def _empty_to_none(v: Any) -> Any:
    """Treat the empty string as "field absent" for optional enum fields.

    The v2 dataset carries empty strings for unset optional enum values
    (e.g. ``"time_lag": ""``); Pydantic would reject those against a
    strict enum. Normalising to ``None`` here keeps the schema strict
    without forcing a data migration before this story lands.
    """
    if isinstance(v, str) and v == "":
        return None
    return v


# ── Node ─────────────────────────────────────────────────────────────


class Node(BaseModel):
    """A node (factor) in the causal graph."""

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    # --- Generic graph-level fields ---
    id: str
    label: str = ""
    definition: str = ""
    domain: str = ""
    level: str = ""

    # --- Project-specific fields (sportdeelname) ---
    bond_influence: BondInfluence | None = None
    disciplines: list[str] = Field(default_factory=list)
    status: NodeStatus | None = None

    # --- Derived metadata (populated by the model-builder, not required) ---
    degree: int | None = None
    in_degree: int | None = None
    out_degree: int | None = None

    @field_validator("bond_influence", "status", mode="before")
    @classmethod
    def _normalize_empty(cls, v: Any) -> Any:
        return _empty_to_none(v)


# ── Edge ─────────────────────────────────────────────────────────────


class Edge(BaseModel):
    """An edge (causal relation, moderation, feedback) in the graph."""

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    # --- Generic graph-level fields ---
    id: str = ""
    source: str
    target: str
    target_type: TargetType = TargetType.NODE
    source_label: str = ""
    target_label: str = ""

    polarity: Polarity | None = None
    strength: Strength | None = None
    base_weight: float | None = None
    edge_type: EdgeType | None = None
    curve_type: CurveType | None = None
    curve_params: dict[str, Any] = Field(default_factory=dict)
    mechanism: str = ""
    literature: list[str] = Field(default_factory=list)

    # --- Project-specific fields (sportdeelname) ---
    cluster: str = ""
    bond_influence: BondInfluence | None = None
    disciplines: list[str] = Field(default_factory=list)
    slider_sensitivity: dict[str, Any] = Field(default_factory=dict)
    time_lag: TimeLag | None = None  # scheduled for removal in S14-03 (Pad B)
    status: NodeStatus | None = None

    @field_validator(
        "polarity",
        "strength",
        "edge_type",
        "curve_type",
        "time_lag",
        "bond_influence",
        "status",
        mode="before",
    )
    @classmethod
    def _normalize_empty(cls, v: Any) -> Any:
        return _empty_to_none(v)

    @field_validator("polarity", mode="before")
    @classmethod
    def _polarity_alias(cls, v: Any) -> Any:
        if isinstance(v, str):
            return _POLARITY_ALIASES.get(v, v)
        return v

    @field_validator("strength", mode="before")
    @classmethod
    def _strength_alias(cls, v: Any) -> Any:
        if isinstance(v, str):
            return _STRENGTH_ALIASES.get(v, v)
        return v

    @field_validator("base_weight")
    @classmethod
    def _base_weight_in_unit_interval(cls, v: float | None) -> float | None:
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError(f"base_weight {v!r} must be in [0.0, 1.0]")
        return v


# ── Graph ────────────────────────────────────────────────────────────


class Graph(BaseModel):
    """A causal graph: metadata + nodes + edges + optional sliders.

    The model-level validator catches dangling ``source``/``target``
    references at load time so they surface as one ``ValidationError``
    instead of a late-binding ``KeyError`` during queries.
    """

    model_config = ConfigDict(extra="allow")

    metadata: dict[str, Any] = Field(default_factory=dict)
    nodes: list[Node]
    edges: list[Edge] = Field(default_factory=list)
    sliders: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_refs(self) -> Graph:
        node_ids: set[str] = {n.id for n in self.nodes}
        edge_ids: set[str] = {e.id for e in self.edges if e.id}

        for e in self.edges:
            who = f"Edge {e.id!r}" if e.id else f"Edge {e.source}→{e.target}"

            if e.source not in node_ids:
                raise ValueError(
                    f"{who}: source {e.source!r} not found in nodes"
                )

            if e.target_type == TargetType.EDGE:
                if e.target not in edge_ids:
                    raise ValueError(
                        f"{who}: moderator target {e.target!r} not found in edges"
                    )
            elif e.target not in node_ids:
                raise ValueError(
                    f"{who}: target {e.target!r} not found in nodes"
                )
        return self
