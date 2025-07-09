from core.qa_agent import QAAgent
from core.docs_agent import DocsAgent
from core.supervisor import Supervisor


class DummyQA(QAAgent):
    def __init__(self):
        self.called = False

    def run(self):
        self.called = True
        return []


class DummyDocs(DocsAgent):
    def __init__(self):
        self.called = False

    def run(self):
        self.called = True
        return []


def test_qa_agent_generates_reports(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("import os\n")
    agent = QAAgent(targets=[str(tmp_path)], report_dir=tmp_path)
    reports = agent.run()
    assert (tmp_path / "bandit.json").exists()
    assert (tmp_path / "pylint.log").exists()
    assert reports


def test_docs_agent_generates_report(tmp_path):
    sample = tmp_path / "sample.py"
    sample.write_text("def foo():\n    pass\n")
    agent = DocsAgent(targets=[str(tmp_path)], report_dir=tmp_path)
    reports = agent.run()
    assert (tmp_path / "docstring.log").exists()
    assert reports


def test_supervisor_dispatch():
    qa = DummyQA()
    docs = DummyDocs()
    sup = Supervisor(qa_agent=qa, docs_agent=docs)
    sup.run(commit_message="bug(core): fix issue")
    assert qa.called and not docs.called

    qa.called = False
    docs.called = False
    sup.run(commit_message="docs(core): update")
    assert docs.called and not qa.called
