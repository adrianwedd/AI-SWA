from __future__ import annotations

from typing import Dict, Iterable


def calculate_reward(
    metrics: Dict[str, float],
    success_weight: float = 1.0,
    runtime_weight: float = 0.1,
) -> float:
    """Return reward based on success and runtime efficiency.

    The function looks for ``success``/``task_success`` and ``runtime``/``duration``
    keys in ``metrics``. If found, the reward is computed as::

        success_weight * success - runtime_weight * runtime

    where ``success`` is interpreted as ``1`` for ``True``/non-zero and ``0`` otherwise.
    When neither value is present, the reward falls back to the sum of all numeric
    metrics.
    """
    success_keys: Iterable[str] = ("success", "task_success")
    runtime_keys: Iterable[str] = ("runtime", "duration")

    success = None
    runtime = None

    for key in success_keys:
        if key in metrics:
            try:
                success = float(metrics[key])
            except Exception:
                success = 0.0
            break

    for key in runtime_keys:
        if key in metrics:
            try:
                runtime = float(metrics[key])
            except Exception:
                runtime = 0.0
            break

    if success is not None or runtime is not None:
        if success is None:
            success = 0.0
        if runtime is None:
            runtime = 0.0
        return success_weight * success - runtime_weight * runtime

    return float(sum(v for v in metrics.values() if isinstance(v, (int, float))))


