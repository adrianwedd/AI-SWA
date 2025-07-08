# Research Brief RB-003: Vision Engine Prioritization

This outline surveys how modern software projects prioritize work and how those ideas could shape the Vision Engine.

## Literature Summary
- **WSJF (Weighted Shortest Job First)** from the Scaled Agile Framework ranks work by dividing business value by job size.
- **Reinforcement learning for scheduling** (e.g., Jaderberg 2017) explores agents that adapt priorities based on observed reward.
- **Multi-criteria decision analysis** methods like AHP compare qualitative factors when quantitative data is sparse.

## Open Questions
- How can WSJF heuristics seed an RL agent without locking in bias?
- What metrics best capture long-term architectural value versus short-term velocity?
- Can feedback from the Reflector Core autonomously refine prioritization weights?

## Implementation Acceptance Criteria
- Future prioritization tasks should implement a baseline WSJF algorithm.
- RL models must ingest Reflector metrics to adjust ranking dynamically.
- Tests should demonstrate improved backlog ordering against historical baselines.
