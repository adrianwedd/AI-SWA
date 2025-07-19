# Reward Strategy Options

This document explores ways to design reward functions for RL-based self-improvement of AI-SWA agents. The aim is to encourage maintainable code and system stability while addressing the open questions in RB-008.

## Addressing RB-008 Questions

### Reward Functions for Maintainable Code
- **Complexity Penalties**: Deduct reward for high cyclomatic complexity using tools like `radon`.
- **Style Enforcement**: Bonus for passing linting and type checks, ensuring clean, consistent code.
- **Documentation Coverage**: Reward when new code includes docstrings and comments compared to total lines changed.
- **Long-Term Stability Metrics**: Incorporate integration test pass rates over time to avoid brittle quick fixes.

### Experience Replay for Sparse Tasks
- Implement a replay buffer to store past transitions from code commits and test outcomes.
- Sample from this buffer when recent tasks provide little signal, stabilizing learning across long gaps.

### Safeguards Against Catastrophic Forgetting
- Maintain a curated dataset of historical successful commits for periodic rehearsal.
- Use a small regularization term that penalizes large policy updates relative to previous parameters.

## Reward Design Comparison

| Approach | Pros | Cons |
| --- | --- | --- |
| **Test-Only Reward** | Simple to implement; ensures functionality | Encourages hacks just to make tests pass |
| **Complexity-Aware Reward** | Promotes clean, readable code | Hard to balance against feature delivery |
| **Stability Score (Integration + Lint + Complexity)** | Combines code quality and operational stability | Requires more metrics collection |
| **Historic Replay with Stability** | Reduces forgetting, maintains quality under sparse updates | Adds storage and compute overhead |

Empirically combining complexity, lint, and long-term test stability provides a balanced reward. Experience replay helps when new tasks are infrequent by reusing past transitions. Regular rehearsal on historical data mitigates catastrophic forgetting.
