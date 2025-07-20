"""Reward helpers for code quality and stability.

This module exposes a ``calculate_reward`` API combining three metrics:
- Complexity penalty computed with ``radon``.
- Linting bonus using ``pylint``.
- Integration test stability from provided test results.

Each component returns a floating point value which is summed to obtain the
final reward.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Mapping

from radon.complexity import cc_visit
from pylint.lint import Run


def complexity_penalty(changeset: Mapping[str, str]) -> float:
    """Return negative penalty based on cyclomatic complexity.

    ``changeset`` maps filenames to their updated source code. Complexity
    is averaged across all functions and scaled down to keep magnitudes small.
    """
    complexities: list[float] = []
    for content in changeset.values():
        try:
            for item in cc_visit(content):
                complexities.append(float(item.complexity))
        except Exception:
            continue
    if not complexities:
        return 0.0
    avg = sum(complexities) / len(complexities)
    return -avg / 10.0


def linting_bonus(changeset: Mapping[str, str]) -> float:
    """Return positive bonus based on pylint score for the changed files."""
    if not changeset:
        return 0.0
    with tempfile.TemporaryDirectory() as tmpdir:
        paths: list[str] = []
        for name, content in changeset.items():
            path = Path(tmpdir) / Path(name).name
            Path(path).write_text(content)
            paths.append(str(path))
        try:
            result = Run(paths, exit=False)
            score = float(getattr(result.linter.stats, "global_note", 0.0))
        except Exception:
            score = 0.0
    return score / 10.0


def integration_stability(results: Mapping[str, float | int]) -> float:
    """Return integration test pass rate from ``results`` mapping."""
    if "integration_pass_rate" in results:
        try:
            return float(results["integration_pass_rate"])
        except Exception:
            return 0.0
    if "passed" in results and "total" in results:
        try:
            total = float(results["total"]) or 1.0
            return float(results["passed"]) / total
        except Exception:
            return 0.0
    if "passed" in results and "failed" in results:
        try:
            total = float(results["passed"]) + float(results["failed"])
            return float(results["passed"]) / (total or 1.0)
        except Exception:
            return 0.0
    return 0.0


def calculate_reward(
    changeset: Mapping[str, str], test_results: Mapping[str, float | int]
) -> float:
    """Return overall reward from lint, complexity and integration metrics."""
    penalty = complexity_penalty(changeset)
    bonus = linting_bonus(changeset)
    stability = integration_stability(test_results)
    return penalty + bonus + stability


__all__ = [
    "calculate_reward",
    "complexity_penalty",
    "linting_bonus",
    "integration_stability",
]
