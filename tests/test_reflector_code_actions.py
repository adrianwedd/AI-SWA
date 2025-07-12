from core.reflector import Reflector
from core.code_llm import CodeLLM
from core.observability import MetricsProvider
from reflector.rl import ReplayBuffer, PPOAgent, ActionGenerator, StateBuilder

class DummyPipe:
    def __call__(self, prompt, max_new_tokens=64, num_return_sequences=1):
        return [{"generated_text": "patch"} for _ in range(num_return_sequences)]

def test_reflector_attaches_code_actions(monkeypatch):
    llm = CodeLLM(pipeline=DummyPipe())
    ref = Reflector(code_model=llm)
    monkeypatch.setattr(ref, "_load_tasks", lambda: [])
    monkeypatch.setattr(ref, "_save_tasks", lambda tasks: None)
    monkeypatch.setattr(ref, "analyze", lambda: {})
    monkeypatch.setattr(ref, "decide", lambda a, t: {"refactor_tasks": [{}],
                                                     "architectural_improvements": [],
                                                     "technical_debt_priorities": [],
                                                     "new_capabilities": [],
                                                     "process_improvements": []})
    monkeypatch.setattr(ref, "execute", lambda d, t: [{"id": 1, "description": "Fix", "component": "c", "dependencies": [], "priority": 1, "status": "pending"}])
    tasks = ref.run_cycle([])
    assert tasks[0]["metadata"]["code_actions"] == ["patch"]


def test_reflector_rl_agent_generates_actions(monkeypatch, tmp_path):
    metrics_file = tmp_path / "m.json"
    metrics_file.write_text("{}")
    provider = MetricsProvider(metrics_file)
    llm = CodeLLM(pipeline=DummyPipe())
    agent = PPOAgent(
        replay_buffer=ReplayBuffer(capacity=1),
        state_builder=StateBuilder(provider),
        action_gen=ActionGenerator(llm=llm),
    )
    ref = Reflector(metrics_provider=provider, rl_agent=agent)
    monkeypatch.setattr(ref, "_load_tasks", lambda: [])
    monkeypatch.setattr(ref, "_save_tasks", lambda tasks: None)
    monkeypatch.setattr(ref, "analyze", lambda: {})
    monkeypatch.setattr(
        ref,
        "decide",
        lambda a, t: {
            "refactor_tasks": [{}],
            "architectural_improvements": [],
            "technical_debt_priorities": [],
            "new_capabilities": [],
            "process_improvements": [],
        },
    )
    monkeypatch.setattr(
        ref,
        "execute",
        lambda d, t: [
            {
                "id": 1,
                "description": "Fix",
                "component": "c",
                "dependencies": [],
                "priority": 1,
                "status": "pending",
            }
        ],
    )
    tasks = ref.run_cycle([])
    assert tasks[0]["metadata"]["code_actions"] == ["patch"]

