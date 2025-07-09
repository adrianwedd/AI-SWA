# Research Brief RB-003: Vision Engine Prioritization

This outline surveys how modern software projects prioritize work and how those ideas could shape the Vision Engine.

## Literature Summary
- **WSJF (Weighted Shortest Job First)** from the Scaled Agile Framework scores each job as `(business value + time criticality + risk reduction) / job size` to maximize value delivered per unit of effort.
- **Reinforcement learning for backlog ordering** (e.g., Jaderberg 2017, Mohr 2021) trains agents that refine priorities based on observed reward signals such as delivery lead time or customer impact.
- **Multi-criteria decision analysis** methods like AHP and MoSCoW compare qualitative factors when quantitative data is sparse.

## Open Questions
- How can WSJF heuristics seed an RL agent without locking in bias toward short-term metrics?
- What reward signals best capture long-term architectural value versus rapid feature delivery?
- Can feedback from the Reflector Core autonomously adjust exploration versus exploitation when prioritizing tasks?

## Implementation Acceptance Criteria
- Provide a baseline WSJF algorithm within the prioritization module.
- Ingest Reflector metrics into an RL model that adapts task ranking over time.
- Demonstrate backlog improvements against historical baselines using tests or simulation.
