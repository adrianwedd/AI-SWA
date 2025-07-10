from core.code_llm import CodeLLM
from reflector.rl.gen_actions import ActionGenerator
from reflector.rl import PPOAgent, ReplayBuffer
from reflector import StateBuilder
from core.observability import MetricsProvider

class DummyPipe:
    def __call__(self, prompt, max_new_tokens=64, num_return_sequences=1):
        return [{"generated_text": "patch"} for _ in range(num_return_sequences)]


class VarPipe:
    def __call__(self, prompt, max_new_tokens=64, num_return_sequences=1):
        return [
            {"generated_text": "x" * (i + 1)} for i in range(num_return_sequences)
        ]


def test_action_generator_produces_patch():
    ag = ActionGenerator(llm=CodeLLM(pipeline=DummyPipe()))
    patches = ag.propose("context")
    assert patches == ["patch"]


def test_filter_and_rank_actions():
    ag = ActionGenerator(llm=CodeLLM(pipeline=VarPipe()))
    patches = ag.propose("ctx", num_actions=3)
    filtered = ag.filter_actions(patches, max_len=2)
    ranked = ag.rank_actions(filtered)
    assert ranked == ["x", "xx"]


def test_ppo_agent_proposes_patch(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"cpu": 0}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buf = ReplayBuffer(capacity=1)
    ag = ActionGenerator(llm=CodeLLM(pipeline=DummyPipe()))
    agent = PPOAgent(replay_buffer=buf, state_builder=builder, action_gen=ag)
    patch = agent.propose_patch("def foo(): pass")
    assert patch == "patch"


def test_ppo_agent_uses_ranked_patch(tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text('{"cpu": 0}')
    provider = MetricsProvider(metrics_file)
    builder = StateBuilder(provider)
    buf = ReplayBuffer(capacity=1)
    ag = ActionGenerator(llm=CodeLLM(pipeline=VarPipe()))
    agent = PPOAgent(replay_buffer=buf, state_builder=builder, action_gen=ag)
    patch = agent.propose_patch("ctx", num_actions=3, max_len=2)
    assert patch == "x"
