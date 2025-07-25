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

## Mutation Parameters

`Gene.mutate()` applies bounded random changes to the hyperparameters:

- **Layer sizes** – each entry in `architecture` may change by ±8 but remains
  within the range of 1–256.
- **Learning rate** – scaled by a factor in [0.8, 1.2] with a lower bound of
  `1e-5`.
- **Clip epsilon** – adjusted by ±0.05 and clipped to the 0.01–1.0 range.
- **Gamma** – adjusted by ±0.05 and clipped to the 0.5–0.999 range.

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

### Example Sweep

The snippet below runs a short evolutionary sweep using the optimizer in
`vision/epo`:

```python
from vision.epo import EvolutionaryPolicyOptimizer, Gene, SimulationEnvironment
from vision.epo.simulation import MetricsProvider
from pathlib import Path

Path("tmp_metrics.json").write_text('{"reward": 1}')
provider = MetricsProvider(Path("tmp_metrics.json"))

env = SimulationEnvironment(metrics_provider=provider, episodes=1)
optimizer = EvolutionaryPolicyOptimizer(environment=env, generations=5)
seed = Gene()
print("Seed gene:", seed)
best = optimizer.evolve(seed)
print("Best gene:", best)
print("History length:", len(optimizer.history))
print(
    "Gene architectures in history:",
    [g.architecture for g in optimizer.history],
)
```

Running it produces output similar to:

```
Seed gene: Gene(architecture=(64,), learning_rate=0.001, clip_epsilon=0.2, gamma=0.99)
Best gene: Gene(architecture=(64,), learning_rate=0.0011, clip_epsilon=0.18388090453334655, gamma=0.999)
History length: 5
Gene architectures in history: [(64,), (64,), (64,), (64,), (64,)]
```

This demonstrates an evolutionary sweep that mutates and evaluates candidate
genes over five generations, returning the best-performing configuration.
