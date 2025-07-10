from reflector.rl import ReplayBuffer, PPOAgent, EWC
import random


def test_replay_buffer_add_and_sample():
    buf = ReplayBuffer(capacity=2)
    buf.add((1, 2))
    buf.add((2, 3))
    buf.add((3, 4))
    assert len(buf) == 2
    sample = buf.sample(1)
    assert len(sample) == 1
    assert sample[0] in [(2, 3), (3, 4)]


def test_ppo_agent_updates_policy_and_clears_buffer():
    random.seed(0)
    buf = ReplayBuffer(capacity=4)
    agent = PPOAgent(replay_buffer=buf)
    state = {"x": 1.0}
    agent.train_step(state, reward=1.0)
    assert len(buf) == 0
    assert agent.policy


def _train(agent: PPOAgent, reward: float, steps: int = 5) -> None:
    state = {"x": 1.0}
    for _ in range(steps):
        agent.train_step(state, reward)


def test_ewc_reduces_catastrophic_forgetting():
    random.seed(0)
    # Agent without EWC
    buf1 = ReplayBuffer(capacity=10)
    agent_no_ewc = PPOAgent(replay_buffer=buf1)
    _train(agent_no_ewc, reward=1.0)
    weight_a = agent_no_ewc.policy.get("x", 0.0)
    _train(agent_no_ewc, reward=-1.0)
    weight_b = agent_no_ewc.policy.get("x", 0.0)
    forgetting_without = abs(weight_b - weight_a)

    # Agent with EWC
    buf2 = ReplayBuffer(capacity=10)
    ewc = EWC()
    agent_ewc = PPOAgent(replay_buffer=buf2, ewc=ewc)
    _train(agent_ewc, reward=1.0)
    agent_ewc.consolidate()
    weight_a_ewc = agent_ewc.policy.get("x", 0.0)
    _train(agent_ewc, reward=-1.0)
    weight_b_ewc = agent_ewc.policy.get("x", 0.0)
    forgetting_with = abs(weight_b_ewc - weight_a_ewc)

    assert forgetting_with < forgetting_without
