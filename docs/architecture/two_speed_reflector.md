# Two-Speed Reflector Coordination

The Reflector core employs a two-speed learning approach. A fast PPO based inner loop continuously refines the current policy while a slower evolutionary outer loop explores new agent architectures. Both loops now share a small scheduler that queues their tasks and executes them in order.

```
+--------------+      +-------------------+
|  PPO Agent   |----->| Shared Scheduler  |<-----+  Evolutionary
+--------------+      +-------------------+      |  Optimizer
                                                 |
                                                 v
                                      +--------------------+
                                      | SimulationEnvironment|
                                      +--------------------+
```

1. **Inner Loop** – The scheduler triggers `engine.inner_step()` which trains the PPO agent using metrics from the `SimulationEnvironment`.
2. **Outer Loop** – After a configurable number of inner steps the scheduler runs `engine.outer_cycle()` to evolve the architecture.
3. **State Rollback** – `SimulationEnvironment.evaluate()` now snapshots simulator state before evaluating each candidate gene and restores it afterwards so every candidate starts from identical conditions.

This coordination ensures consistent evaluation and simplifies integrating additional background tasks in future revisions.

## Gene Structure

Each outer-loop iteration manipulates a **gene** representing key PPO hyperparameters:

- `architecture` – tuple of hidden layer sizes for the policy network.
- `learning_rate` – shared learning rate for actor and critic updates.
- `clip_epsilon` – clipping range for PPO updates.
- `gamma` – discount factor applied to rewards.

### Introducing New Gene Configurations

`EvolutionaryPolicyOptimizer` generates new candidates by calling
`Gene.mutate()` and `Gene.crossover()`. After evaluation the winning gene can
be persisted with `Gene.to_json()` and reloaded via `Gene.from_json()` on the
next run, allowing evolution to resume from the most successful configuration.

## Validation

The `tests/test_two_speed_vs_ppo.py` suite runs a minimal evolution cycle and
asserts that the evolved gene yields a higher reward than the initial PPO
configuration. This confirms the hand-off between loops and demonstrates an
immediate benefit over PPO-only training.
