from core.reflector import Reflector
from core.code_llm import CodeLLM

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

