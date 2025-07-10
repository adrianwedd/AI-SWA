from __future__ import annotations

"""Reward calculation helpers for RL training."""

from typing import Dict, Tuple

# Default weights for each reward component
DEFAULT_WEIGHTS = {
    "correctness": 1.0,
    "performance": 0.5,
    "style": 0.2,
}


def reward_terms(metrics: Dict[str, float]) -> Dict[str, float]:
    """Extract reward components from ``metrics``.

    - ``correctness`` derives from ``success`` or ``task_success``.
    - ``performance`` is the negative runtime or duration.
    - ``style`` uses ``style`` or ``style_score`` metrics.
    """
    correctness_keys = ("correctness", "success", "task_success")
    runtime_keys = ("runtime", "duration")
    style_keys = ("style", "style_score")

    correctness = 0.0
    for key in correctness_keys:
        if key in metrics:
            try:
                correctness = float(metrics[key])
            except Exception:
                correctness = 1.0 if metrics[key] else 0.0
            break

    performance = 0.0
    for key in runtime_keys:
        if key in metrics:
            try:
                performance = -float(metrics[key])
            except Exception:
                performance = 0.0
            break

    style = 0.0
    for key in style_keys:
        if key in metrics:
            try:
                style = float(metrics[key])
            except Exception:
                style = 0.0
            break

    return {
        "correctness": correctness,
        "performance": performance,
        "style": style,
    }


def calculate_reward(
    metrics: Dict[str, float], weights: Dict[str, float] | None = None
) -> Tuple[float, Dict[str, float]]:
    """Return weighted reward and component terms."""
    terms = reward_terms(metrics)
    w = weights or DEFAULT_WEIGHTS
    reward = sum(w.get(k, 0.0) * v for k, v in terms.items())
    return reward, terms

__all__ = ["reward_terms", "calculate_reward", "DEFAULT_WEIGHTS"]
