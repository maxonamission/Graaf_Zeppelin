"""
Slider Engine — Curve functions and simulation for policy sliders.

Each slider modifies edge weights in the causal graph according to
a curve function (dampening threshold, inverted-U, or linear).
"""

from __future__ import annotations

import math
from typing import Any


def dampening_threshold(value: float, t: float, b: float) -> float:
    """Sigmoid-like dampening above a threshold.

    Below the threshold, output ≈ 1 (no dampening).
    Above the threshold, output drops toward 0.

    Args:
        value: Slider value (0–1).
        t: Threshold point.
        b: Steepness of the sigmoid.

    Returns:
        Multiplier in [0, 1].
    """
    return 1.0 / (1.0 + math.exp(b * (value - t)))


def inverted_u(value: float, mu: float, sigma: float) -> float:
    """Gaussian curve with an optimum — too little and too much are both bad.

    Args:
        value: Slider value (0–1).
        mu: Optimum point.
        sigma: Width of the curve.

    Returns:
        Multiplier in [0, 1].
    """
    return math.exp(-0.5 * ((value - mu) / sigma) ** 2)


def linear_mod(value: float, gamma: float) -> float:
    """Linear scaling around the midpoint (0.5).

    Args:
        value: Slider value (0–1).
        gamma: Sensitivity coefficient.

    Returns:
        Multiplier around 1.0.
    """
    return 1.0 + gamma * (value - 0.5)


# Curve type registry
_CURVE_FUNCTIONS = {
    "DAMPENING_THRESHOLD": dampening_threshold,
    "INVERTED_U_MOD": inverted_u,
    "LINEAR_MOD": linear_mod,
}


def compute_slider_multiplier(slider: dict[str, Any], value: float) -> float:
    """Compute the edge-weight multiplier for a slider at a given value.

    Args:
        slider: Slider definition from the graph model.
        value: Desired slider position (0–1).

    Returns:
        Multiplier to apply to affected edge weights.
    """
    curve_type = slider.get("curve_type", "")
    curve_fn = _CURVE_FUNCTIONS.get(curve_type)
    if curve_fn is None:
        return 1.0

    params = slider.get("curve_params", {})
    if curve_type == "DAMPENING_THRESHOLD":
        return curve_fn(value, t=params.get("t", 0.5), b=params.get("b", 5))
    elif curve_type == "INVERTED_U_MOD":
        return curve_fn(value, mu=params.get("mu", 0.5), sigma=params.get("sigma", 0.3))
    elif curve_type == "LINEAR_MOD":
        return curve_fn(value, gamma=params.get("gamma", 0.3))
    return 1.0


# Sensitivity level to numeric weight
_SENSITIVITY_WEIGHT = {
    "very_high": 1.0,
    "high": 0.75,
    "medium": 0.5,
    "low": 0.25,
    "none": 0.0,
}


def apply_slider(
    slider: dict[str, Any],
    value: float,
    edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply a slider at a given value to a list of edges.

    Returns edges with modified weights based on slider sensitivity.

    Args:
        slider: Slider definition.
        value: Slider position (0–1).
        edges: List of edge dicts (must include slider_sensitivity and strength).

    Returns:
        List of dicts with edge info and adjusted weights.
    """
    multiplier = compute_slider_multiplier(slider, value)
    sensitivity_key = slider.get("sensitivity_key", "")
    default_multiplier = compute_slider_multiplier(slider, slider.get("default", 0.5))

    results = []
    for edge in edges:
        sens_map = edge.get("slider_sensitivity", {})
        sens_level = sens_map.get(sensitivity_key, "none")
        sens_weight = _SENSITIVITY_WEIGHT.get(sens_level, 0.0)

        if sens_weight == 0.0:
            continue

        original_strength = edge.get("strength", 0.5)
        # Relative change from default position
        relative_change = multiplier / default_multiplier if default_multiplier > 0 else multiplier

        # Blend: full sensitivity means full multiplier effect
        blended = 1.0 + sens_weight * (relative_change - 1.0)
        adjusted_strength = max(0.0, min(1.0, original_strength * blended))

        results.append(
            {
                "edge_id": edge.get("id", ""),
                "source": edge.get("cause", edge.get("source", "")),
                "target": edge.get("effect", edge.get("target", "")),
                "source_label": edge.get("source_label", ""),
                "target_label": edge.get("target_label", ""),
                "original_strength": original_strength,
                "adjusted_strength": round(adjusted_strength, 4),
                "sensitivity": sens_level,
                "multiplier": round(blended, 4),
            }
        )

    results.sort(key=lambda x: abs(x["adjusted_strength"] - x["original_strength"]), reverse=True)
    return results


def simulate_sliders(
    sliders_config: list[dict[str, Any]],
    slider_values: dict[str, float],
    edges: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Apply multiple sliders simultaneously and return combined effects.

    Args:
        sliders_config: All slider definitions from the model.
        slider_values: Dict of {slider_id: value} to apply.
        edges: All edges from the graph.

    Returns:
        List of affected edges with combined adjusted weights.
    """
    # Start with original strengths
    combined: dict[str, dict[str, Any]] = {}

    for slider in sliders_config:
        sid = slider.get("id", "")
        if sid not in slider_values:
            continue

        value = slider_values[sid]
        affected = apply_slider(slider, value, edges)

        for result in affected:
            eid = result["edge_id"]
            if eid not in combined:
                combined[eid] = {
                    **result,
                    "applied_sliders": [],
                }
            else:
                # Multiply adjustments
                prev = combined[eid]["adjusted_strength"]
                ratio = (
                    result["adjusted_strength"] / result["original_strength"]
                    if result["original_strength"] > 0
                    else 1.0
                )
                combined[eid]["adjusted_strength"] = round(max(0.0, min(1.0, prev * ratio)), 4)

            combined[eid]["applied_sliders"].append(
                {
                    "slider_id": sid,
                    "slider_label": slider.get("label", ""),
                    "value": value,
                    "individual_multiplier": result["multiplier"],
                }
            )

    results = list(combined.values())
    results.sort(key=lambda x: abs(x["adjusted_strength"] - x["original_strength"]), reverse=True)
    return results
