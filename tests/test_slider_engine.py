"""Tests for the slider simulation engine."""

import pytest

from app.core.slider_engine import (
    apply_slider,
    compute_slider_multiplier,
    dampening_threshold,
    inverted_u,
    linear_mod,
    simulate_sliders,
)


class TestCurveFunctions:
    def test_dampening_threshold_below(self):
        """Below threshold → multiplier close to 1 (no dampening)."""
        result = dampening_threshold(0.2, t=0.55, b=5)
        assert result > 0.8

    def test_dampening_threshold_above(self):
        """Well above threshold → multiplier close to 0 (strong dampening)."""
        result = dampening_threshold(0.9, t=0.55, b=5)
        assert result < 0.2

    def test_dampening_threshold_at_threshold(self):
        """At threshold → multiplier = 0.5."""
        result = dampening_threshold(0.55, t=0.55, b=5)
        assert abs(result - 0.5) < 0.01

    def test_inverted_u_at_optimum(self):
        """At optimum → multiplier = 1.0."""
        result = inverted_u(0.55, mu=0.55, sigma=0.3)
        assert abs(result - 1.0) < 0.01

    def test_inverted_u_away_from_optimum(self):
        """Far from optimum → multiplier drops."""
        result = inverted_u(0.0, mu=0.55, sigma=0.3)
        assert result < 0.3

    def test_inverted_u_symmetric(self):
        """Equal distance from optimum → equal multiplier."""
        left = inverted_u(0.3, mu=0.55, sigma=0.3)
        right = inverted_u(0.8, mu=0.55, sigma=0.3)
        assert abs(left - right) < 0.01

    def test_linear_mod_at_midpoint(self):
        """At 0.5 → multiplier = 1.0."""
        result = linear_mod(0.5, gamma=0.3)
        assert abs(result - 1.0) < 0.01

    def test_linear_mod_above(self):
        """Above midpoint → multiplier > 1."""
        result = linear_mod(0.8, gamma=0.3)
        assert result > 1.0

    def test_linear_mod_below(self):
        """Below midpoint → multiplier < 1."""
        result = linear_mod(0.2, gamma=0.3)
        assert result < 1.0


class TestComputeSliderMultiplier:
    def test_unknown_curve(self):
        """Unknown curve type → multiplier = 1.0."""
        slider = {"curve_type": "UNKNOWN", "curve_params": {}}
        assert compute_slider_multiplier(slider, 0.5) == 1.0

    def test_linear_mod_slider(self):
        slider = {
            "curve_type": "LINEAR_MOD",
            "curve_params": {"gamma": 0.3},
        }
        result = compute_slider_multiplier(slider, 0.8)
        assert result > 1.0

    def test_dampening_slider(self):
        slider = {
            "curve_type": "DAMPENING_THRESHOLD",
            "curve_params": {"t": 0.55, "b": 5},
        }
        result = compute_slider_multiplier(slider, 0.2)
        assert result > 0.8


class TestApplySlider:
    def test_applies_to_sensitive_edges(self):
        slider = {
            "id": "S01",
            "label": "Test",
            "curve_type": "LINEAR_MOD",
            "curve_params": {"gamma": 0.4},
            "default": 0.5,
            "sensitivity_key": "sens_eco",
        }
        edges = [
            {
                "id": "E-MED-001",
                "cause": "A",
                "effect": "B",
                "strength": 0.8,
                "slider_sensitivity": {"sens_eco": "high"},
            },
            {
                "id": "E-STR-001",
                "cause": "C",
                "effect": "D",
                "strength": 0.5,
                "slider_sensitivity": {"sens_eco": "none"},
            },
        ]
        results = apply_slider(slider, 0.8, edges)
        # Only E001 should be affected (E002 has sensitivity "none")
        assert len(results) == 1
        assert results[0]["edge_id"] == "E-MED-001"
        # Slider > default → strength should increase
        assert results[0]["adjusted_strength"] > 0.8

    def test_no_effect_at_default(self):
        slider = {
            "id": "S01",
            "curve_type": "LINEAR_MOD",
            "curve_params": {"gamma": 0.3},
            "default": 0.5,
            "sensitivity_key": "sens_test",
        }
        edges = [
            {
                "id": "E-MED-001",
                "strength": 0.6,
                "slider_sensitivity": {"sens_test": "high"},
            },
        ]
        results = apply_slider(slider, 0.5, edges)
        # At default value, no change expected
        assert len(results) == 1
        assert abs(results[0]["adjusted_strength"] - 0.6) < 0.01


class TestSimulateSliders:
    def test_multiple_sliders(self):
        sliders = [
            {
                "id": "S01",
                "label": "Slider 1",
                "curve_type": "LINEAR_MOD",
                "curve_params": {"gamma": 0.4},
                "default": 0.5,
                "sensitivity_key": "sens_a",
            },
            {
                "id": "S02",
                "label": "Slider 2",
                "curve_type": "LINEAR_MOD",
                "curve_params": {"gamma": 0.3},
                "default": 0.5,
                "sensitivity_key": "sens_b",
            },
        ]
        edges = [
            {
                "id": "E-MED-001",
                "strength": 0.6,
                "slider_sensitivity": {"sens_a": "high", "sens_b": "medium"},
            },
        ]
        results = simulate_sliders(sliders, {"S01": 0.8, "S02": 0.7}, edges)
        assert len(results) == 1
        assert len(results[0]["applied_sliders"]) == 2

    def test_no_matching_sliders(self):
        sliders = [
            {
                "id": "S01",
                "curve_type": "LINEAR_MOD",
                "curve_params": {"gamma": 0.3},
                "default": 0.5,
                "sensitivity_key": "sens_a",
            },
        ]
        edges = [
            {
                "id": "E-MED-001",
                "strength": 0.6,
                "slider_sensitivity": {"sens_a": "none"},
            },
        ]
        results = simulate_sliders(sliders, {"S01": 0.8}, edges)
        assert len(results) == 0
