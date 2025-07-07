# RL vs WSJF Integration Test Results

Integration tests were added to verify the Vision Engine's reinforcement-learning component can alter task prioritization compared to the Weighted Shortest Job First (WSJF) baseline.

The test executes the Vision Engine twice:
1. Using only WSJF scoring.
2. With a simple RL agent that reverses the task order and runs with full authority.

The RL run produces a different ordering and records the comparison in a history file. This confirms that RL-driven prioritization can diverge from the baseline and that the logging mechanism works.
