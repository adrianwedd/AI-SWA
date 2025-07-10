from core.code_llm import CodeLLM
from vision.vision_engine import RLAgent


class DummyPipe:
    def __call__(self, prompt, max_new_tokens=64, num_return_sequences=1):
        return [{"generated_text": f"{prompt}-action"} for _ in range(num_return_sequences)]


def test_code_llm_generates_actions():
    llm = CodeLLM(pipeline=DummyPipe())
    actions = llm.generate_actions("def foo(): pass", max_tokens=10)
    assert actions == ["def foo(): pass-action"]


def test_rl_agent_generates_actions():
    llm = CodeLLM(pipeline=DummyPipe())
    agent = RLAgent(code_model=llm)
    actions = agent.generate_code_actions("print('hi')", num_return_sequences=2)
    assert actions == ["print('hi')-action", "print('hi')-action"]
