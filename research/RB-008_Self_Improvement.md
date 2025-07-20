# Research Brief RB-008: Self-Improvement Optimization

Continuous self-improvement is a key differentiator of AI-SWA. This outline surveys approaches for automated learning loops.

## Literature Summary
- **Proximal Policy Optimization (PPO)** is a stable reinforcement learning algorithm for training code-generating agents.
- **Evolutionary strategies** can explore large policy spaces without gradient information.
- **Self-play and curriculum learning** gradually increase difficulty to improve sample efficiency.

## Open Questions
- How do we design reward functions that encourage maintainable code, not just passing tests?
- Could experience replay stabilize learning when tasks are sparse?
- What safeguards prevent catastrophic forgetting during continual updates?

## Implementation Acceptance Criteria
- Implement a replay buffer and curriculum generator informed by this research.
- Evaluate agents against historical commits to measure improvement.
- Provide rollback mechanisms if performance degrades.

## Replay Buffer Usage
Experience tuples collected during reflection cycles can now be persisted to disk.
`reflector.rl.replay_buffer.ReplayBuffer` accepts a `path` argument. When
provided, transitions are saved as JSON each time ``add()`` is called and the
buffer automatically reloads existing data on initialization. The PPO agent in
`reflector.rl.training` loads these prior experiences at startup so training can
resume across runs.
