"""Tests for app.core.id_schema (S14-05)."""

from __future__ import annotations

import pytest

from app.core.id_schema import (
    DOMAIN_ABBR,
    EDGE_TYPE_ABBR,
    EdgeIdParts,
    NodeIdParts,
    derive_edge_id,
    derive_node_id,
    normalize_level,
    parse_edge_id,
    parse_node_id,
    validate_edge_id,
    validate_node_id,
)


# ── Tables are the source of truth ──────────────────────────────────


class TestTables:
    def test_domain_table_has_nine_entries(self):
        assert len(DOMAIN_ABBR) == 9

    def test_edge_type_table_has_five_entries(self):
        assert len(EDGE_TYPE_ABBR) == 5

    def test_all_abbreviations_unique(self):
        assert len(set(DOMAIN_ABBR.values())) == len(DOMAIN_ABBR)
        assert len(set(EDGE_TYPE_ABBR.values())) == len(EDGE_TYPE_ABBR)

    def test_domain_abbreviations_are_three_letters(self):
        for abbr in DOMAIN_ABBR.values():
            assert len(abbr) == 3, f"{abbr!r} is not 3 letters"
            assert abbr.isupper()


# ── normalize_level ──────────────────────────────────────────────────


class TestNormalizeLevel:
    @pytest.mark.parametrize(
        ("input_level", "id_level"),
        [
            ("L0", "L0"),
            ("L1", "L1"),
            ("L1/L2", "L12"),
            ("L2", "L2"),
            ("L3", "L3"),
        ],
    )
    def test_levels(self, input_level: str, id_level: str):
        assert normalize_level(input_level) == id_level


# ── derive_* ─────────────────────────────────────────────────────────


class TestDeriveNodeId:
    def test_example_from_docs(self):
        assert derive_node_id("Uitkomsten", "L0", 1) == "UIT-L0-001"

    def test_level_normalisation(self):
        assert derive_node_id("Sociaal", "L1/L2", 5) == "SOC-L12-005"

    def test_seq_zero_padded(self):
        assert derive_node_id("Macro-context", "L3", 42) == "MAC-L3-042"
        assert derive_node_id("Macro-context", "L3", 100) == "MAC-L3-100"

    def test_unknown_domain(self):
        with pytest.raises(KeyError, match="Unknown domain"):
            derive_node_id("Marsmannetjes", "L0", 1)

    def test_invalid_seq(self):
        with pytest.raises(ValueError, match="seq"):
            derive_node_id("Uitkomsten", "L0", 0)


class TestDeriveEdgeId:
    def test_examples_from_docs(self):
        assert derive_edge_id("MEDIATING", 14) == "E-MED-014"
        assert derive_edge_id("FEEDBACK", 7) == "E-FBK-007"
        assert derive_edge_id("SOCIAL_REGULATORY", 3) == "E-SREG-003"

    def test_unknown_edge_type(self):
        with pytest.raises(KeyError, match="Unknown edge_type"):
            derive_edge_id("TELEPATHIC", 1)


# ── validate_* ───────────────────────────────────────────────────────


class TestValidateNodeId:
    @pytest.mark.parametrize(
        "id",
        ["UIT-L0-001", "TRP-L1-012", "SOC-L12-005", "MAC-L3-042"],
    )
    def test_valid(self, id: str):
        assert validate_node_id(id) is True

    @pytest.mark.parametrize(
        "id",
        [
            "N001",              # legacy
            "XYZ-L0-001",        # unknown domain abbreviation
            "UIT-L4-001",        # unknown level
            "UIT-l0-001",        # lowercase level
            "uit-L0-001",        # lowercase domain
            "UIT-L0-1",          # seq not zero-padded
            "UIT-L0",            # missing seq
            "UIT-L0-001-extra",  # trailing junk
            "",
        ],
    )
    def test_invalid(self, id: str):
        assert validate_node_id(id) is False


class TestValidateEdgeId:
    @pytest.mark.parametrize(
        "id",
        ["E-MED-014", "E-FBK-007", "E-STR-001", "E-MOD-999", "E-SREG-042"],
    )
    def test_valid(self, id: str):
        assert validate_edge_id(id) is True

    @pytest.mark.parametrize(
        "id",
        [
            "E001",
            "E-UNK-001",
            "E-med-001",
            "E-MED-1",
            "X-MED-001",
            "",
        ],
    )
    def test_invalid(self, id: str):
        assert validate_edge_id(id) is False


# ── parse_* ──────────────────────────────────────────────────────────


class TestParseNodeId:
    def test_parse_round_trip(self):
        parts = parse_node_id("UIT-L0-001")
        assert parts == NodeIdParts(
            domain_abbr="UIT", domain="Uitkomsten", level="L0", seq=1
        )

    def test_parse_normalised_level(self):
        parts = parse_node_id("SOC-L12-005")
        assert parts.level == "L12"
        assert parts.seq == 5

    def test_parse_invalid_shape(self):
        with pytest.raises(ValueError, match="does not match pattern"):
            parse_node_id("N001")

    def test_parse_unknown_domain(self):
        """The regex's domain alternation excludes unknown abbreviations,
        so we get the pattern-mismatch error rather than a separate
        'unknown domain' error. Both signal the same problem — we check
        for the node-ID pattern wording."""
        with pytest.raises(ValueError, match="does not match pattern"):
            parse_node_id("ABC-L0-001")


class TestParseEdgeId:
    def test_parse_round_trip(self):
        parts = parse_edge_id("E-MED-014")
        assert parts == EdgeIdParts(
            edge_type_abbr="MED", edge_type="MEDIATING", seq=14
        )

    def test_parse_feedback(self):
        parts = parse_edge_id("E-FBK-007")
        assert parts.edge_type == "FEEDBACK"

    def test_parse_invalid(self):
        with pytest.raises(ValueError):
            parse_edge_id("E001")
