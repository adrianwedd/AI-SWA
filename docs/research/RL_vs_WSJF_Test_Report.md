# RL vs WSJF Integration Test Results

Integration tests were added to verify the Vision Engine's reinforcement-learning component can alter task prioritization compared to the Weighted Shortest Job First (WSJF) baseline.

The test executes the Vision Engine twice:
1. Using only WSJF scoring.
2. With a simple RL agent that reverses the task order and runs with full authority.

The RL run produces a different ordering and records the comparison in a history file. This confirms that RL-driven prioritization can diverge from the baseline and that the logging mechanism works.

Example ordering from the integration test:
- WSJF baseline order: ``[2, 1, 3]`` with scores ``[3.5, 2.6, 2.0]``
- RL refined order: ``[3, 1, 2]`` with scores ``[2.0, 2.6, 3.5]``

## Additional Test Coverage

The RL training suite (`tests/test_rl_training.py`) ensures that metrics collected during
experiment runs are persisted for offline analysis. It also verifies that rewards are
calculated correctly and that replay buffers receive recorded samples. All tests pass,
confirming that the RL agent integrates with the observability layer.

