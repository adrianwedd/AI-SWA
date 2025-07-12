"""Export state/action pairs from simulation runs for offline RL training."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from simulator.code_env import CodeEnv, Service, Database, LoadBalancer
from core.production_simulator import SimulationMetricsProvider
from reflector.state_builder import StateBuilder
from reflector.rl.ppo_agent import PPOAgent
from reflector.rl.replay_buffer import ReplayBuffer


def build_env(workload: Path) -> CodeEnv:
    env = CodeEnv(workload_path=workload)
    env.add_service(Service(name="api", capacity=1))
    env.add_database(Database(name="db", max_connections=1))
    env.add_load_balancer(LoadBalancer(name="lb", targets=[env.simulator.services["api"]]))
    return env


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination JSONL file")
    parser.add_argument("--steps", type=int, default=100, help="Simulation steps")
    parser.add_argument("--workload", type=Path, default=Path("workload.json"))
    args = parser.parse_args()

    env = build_env(args.workload)
    provider = SimulationMetricsProvider(env.simulator)
    builder = StateBuilder(provider)
    agent = PPOAgent(replay_buffer=ReplayBuffer(capacity=8), state_builder=builder)

    dataset = []
    for _ in range(args.steps):
        state = builder.build()
        action, _ = agent.select_action(state)
        env.step({"scale_service": {"name": "api", "delta": action}})
        dataset.append({"state": state, "action": action})

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as fh:
        for row in dataset:
            fh.write(json.dumps(row) + "\n")


if __name__ == "__main__":  # pragma: no cover - CLI tool
    main()
