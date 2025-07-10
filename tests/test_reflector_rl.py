from reflector.rl import ReplayBuffer, PPOAgent
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
