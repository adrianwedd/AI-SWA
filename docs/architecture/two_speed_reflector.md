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
