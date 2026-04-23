"""ID-schema voor nodes en edges (S14-05).

Conventie (Vorm A, vastgelegd in ``stories/done/S14-05-id-schema-herontwerp.md``):

    Nodes:  {DOMEIN-AFK}-{NIVEAU}-{VOLGNR}   bv. UIT-L0-001, TRP-L1-012
    Edges:  E-{EDGE_TYPE_AFK}-{VOLGNR}       bv. E-MED-014, E-FBK-007

Domein-afkortingen zijn 3 letters (NL). Edge-afkortingen komen uit de
bestaande EN ``edge_type``-enum. Het niveau ``L1/L2`` wordt in de ID
genormaliseerd tot ``L12`` (fixed-width, prettig sorteerbaar); het
``level``-veld op de node zelf blijft ongewijzigd — de ID is een
*afgeleide* weergave, geen vervanging.

De tabellen hieronder zijn bindend voor de data onder ``data/models/``.
Nieuwe domeinen / edge-types moeten hier expliciet worden toegevoegd.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ── Tabellen (bindend voor deze epic) ────────────────────────────────

DOMAIN_ABBR: dict[str, str] = {
    "Uitkomsten": "UIT",
    "Regels & Administratie": "REG",
    "Sociaal": "SOC",
    "Psychologisch": "PSY",
    "Middelen & Logistiek": "MDL",
    "Organisatie & Aanbod": "ORG",
    "Training & Prestatie": "TRP",
    "Macro-context": "MAC",
    "Discipline-specifiek": "DIS",
}

EDGE_TYPE_ABBR: dict[str, str] = {
    "STRUCTURAL": "STR",
    "MEDIATING": "MED",
    "MODERATOR": "MOD",
    "FEEDBACK": "FBK",
    "SOCIAL_REGULATORY": "SREG",
}

# Niveau-normalisatie: "L1/L2" (datatekst) → "L12" (ID-segment).
LEVEL_NORMALIZE: dict[str, str] = {"L1/L2": "L12"}

# Reverse lookups, afgeleid uit de primaire tabellen.
_ABBR_TO_DOMAIN: dict[str, str] = {v: k for k, v in DOMAIN_ABBR.items()}
_ABBR_TO_EDGE_TYPE: dict[str, str] = {v: k for k, v in EDGE_TYPE_ABBR.items()}

# Regex voor full-form-validatie.
_DOMAIN_PATTERN = "|".join(re.escape(a) for a in DOMAIN_ABBR.values())
_EDGE_TYPE_PATTERN = "|".join(re.escape(a) for a in EDGE_TYPE_ABBR.values())
_LEVEL_PATTERN = r"L(?:0|1|12|2|3)"
_NODE_ID_RE = re.compile(
    rf"^(?P<domain>{_DOMAIN_PATTERN})-(?P<level>{_LEVEL_PATTERN})-(?P<seq>\d{{3,}})$"
)
_EDGE_ID_RE = re.compile(rf"^E-(?P<edge_type>{_EDGE_TYPE_PATTERN})-(?P<seq>\d{{3,}})$")


# ── Parse-result-containers ──────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class NodeIdParts:
    """Decomposed components of a node ID."""

    domain_abbr: str
    domain: str
    level: str  # ID-level (e.g. "L12", not "L1/L2")
    seq: int


@dataclass(frozen=True, slots=True)
class EdgeIdParts:
    """Decomposed components of an edge ID."""

    edge_type_abbr: str
    edge_type: str
    seq: int


# ── Publieke API ─────────────────────────────────────────────────────


def normalize_level(level: str) -> str:
    """Map a data-level to its ID-level (``L1/L2`` → ``L12``, others unchanged)."""
    return LEVEL_NORMALIZE.get(level, level)


def domain_abbr_for(domain: str) -> str:
    """Return the 3-letter abbreviation for a domain name.

    Raises ``KeyError`` if the domain is not in the canonical table.
    """
    try:
        return DOMAIN_ABBR[domain]
    except KeyError as exc:
        raise KeyError(
            f"Unknown domain {domain!r}; expected one of {sorted(DOMAIN_ABBR)}"
        ) from exc


def edge_type_abbr_for(edge_type: str) -> str:
    """Return the abbreviation for an edge_type enum value."""
    try:
        return EDGE_TYPE_ABBR[edge_type]
    except KeyError as exc:
        raise KeyError(
            f"Unknown edge_type {edge_type!r}; expected one of {sorted(EDGE_TYPE_ABBR)}"
        ) from exc


def derive_node_id(domain: str, level: str, seq: int) -> str:
    """Build a node ID from domain, level and sequence number."""
    if seq < 1:
        raise ValueError(f"seq must be >= 1, got {seq}")
    return f"{domain_abbr_for(domain)}-{normalize_level(level)}-{seq:03d}"


def derive_edge_id(edge_type: str, seq: int) -> str:
    """Build an edge ID from edge_type and sequence number."""
    if seq < 1:
        raise ValueError(f"seq must be >= 1, got {seq}")
    return f"E-{edge_type_abbr_for(edge_type)}-{seq:03d}"


def validate_node_id(id: str) -> bool:
    """Return True iff ``id`` matches the node-ID pattern with known parts."""
    m = _NODE_ID_RE.match(id)
    if m is None:
        return False
    return m.group("domain") in _ABBR_TO_DOMAIN


def validate_edge_id(id: str) -> bool:
    """Return True iff ``id`` matches the edge-ID pattern with a known type."""
    m = _EDGE_ID_RE.match(id)
    if m is None:
        return False
    return m.group("edge_type") in _ABBR_TO_EDGE_TYPE


def parse_node_id(id: str) -> NodeIdParts:
    """Decompose a node ID. Raises ``ValueError`` with a helpful message on failure."""
    m = _NODE_ID_RE.match(id)
    if not m:
        raise ValueError(
            f"Node ID {id!r} does not match pattern "
            f"'{{DOMAIN-AFK}}-{{LEVEL}}-{{VOLGNR}}' (e.g. 'UIT-L0-001')"
        )
    abbr = m.group("domain")
    if abbr not in _ABBR_TO_DOMAIN:
        raise ValueError(
            f"Node ID {id!r} has unknown domain abbreviation {abbr!r}; "
            f"expected one of {sorted(_ABBR_TO_DOMAIN)}"
        )
    return NodeIdParts(
        domain_abbr=abbr,
        domain=_ABBR_TO_DOMAIN[abbr],
        level=m.group("level"),
        seq=int(m.group("seq")),
    )


def parse_edge_id(id: str) -> EdgeIdParts:
    """Decompose an edge ID. Raises ``ValueError`` on failure."""
    m = _EDGE_ID_RE.match(id)
    if not m:
        raise ValueError(
            f"Edge ID {id!r} does not match pattern 'E-{{TYPE-AFK}}-{{VOLGNR}}' (e.g. 'E-MED-014')"
        )
    abbr = m.group("edge_type")
    if abbr not in _ABBR_TO_EDGE_TYPE:
        raise ValueError(
            f"Edge ID {id!r} has unknown edge_type abbreviation {abbr!r}; "
            f"expected one of {sorted(_ABBR_TO_EDGE_TYPE)}"
        )
    return EdgeIdParts(
        edge_type_abbr=abbr,
        edge_type=_ABBR_TO_EDGE_TYPE[abbr],
        seq=int(m.group("seq")),
    )
