import yaml  # noqa: E402
import logging
import pytest
from core.reflector import Reflector  # noqa: E402


def test_reflector_creates_task(tmp_path):
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(
        "- id: 1\n"
        "  description: base\n"
        "  component: core\n"
        "  dependencies: []\n"
        "  priority: 1\n"
        "  status: pending\n"
    )
    code_file = tmp_path / "complex.py"
    code_file.write_text("""\
def func(x):
    if x > 0:
        if x > 1:
            return 1
        else:
            return 2
    else:
        return 3
""")
    refl = Reflector(tasks_path=tasks_file, complexity_threshold=1, analysis_paths=[code_file])
    tasks = yaml.safe_load(tasks_file.read_text())
    result = refl.run_cycle(tasks)
    assert isinstance(result, list)
    updated = yaml.safe_load(tasks_file.read_text())
    assert isinstance(updated, list)

from core.observability import MetricsProvider


def test_reflector_collects_metrics(tmp_path):
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(
        "- id: 1\n"
        "  description: base\n"
        "  component: core\n"
        "  dependencies: []\n"
        "  priority: 1\n"
        "  status: pending\n"
    )
    code_file = tmp_path / "code.py"
    code_file.write_text("def foo():\n    return 1\n")
    metrics_file = tmp_path / "metrics.json"
    metrics_file.write_text('{"coverage": 90}')

    provider = MetricsProvider(metrics_file)
    refl = Reflector(
        tasks_path=tasks_file,
        complexity_threshold=1,
        analysis_paths=[code_file],
        metrics_provider=provider,
    )
    analysis = refl.analyze()
    assert analysis.get("observability_metrics") == {"coverage": 90}


def test_load_tasks_failures(tmp_path, caplog):
    missing = tmp_path / "missing.yml"
    refl = Reflector(tasks_path=missing)
    with caplog.at_level(logging.WARNING):
        assert refl._load_tasks() == []

    bad = tmp_path / "bad.yml"
    bad.write_text(": - invalid")
    with caplog.at_level(logging.ERROR):
        assert refl._load_tasks() == []


def test_validate_detects_issues():
    refl = Reflector()
    tasks = [
        {"id": 1, "description": "a", "component": "c", "dependencies": [], "priority": 1, "status": "pending"},
        {"id": 1, "description": "b", "component": "c", "dependencies": [], "priority": 1, "status": "pending"},
    ]
    with pytest.raises(ValueError):
        refl.validate(tasks)


def test_summarize_code_metrics_distribution():
    refl = Reflector(complexity_threshold=10)
    metrics = {
        "a.py": {"max_complexity": 5, "needs_refactor": True},
        "b.py": {"max_complexity": 20},
        "c.py": {"max_complexity": 30},
    }
    summary = refl._summarize_code_metrics(metrics)
    assert summary["total_files"] == 3
    assert summary["files_needing_refactor"] == 1
    assert summary["complexity_distribution"]["critical"] == 1
    assert summary["complexity_distribution"]["high"] == 1
    assert summary["complexity_distribution"]["low"] == 1
    assert summary["needs_attention"] is True


def test_analyze_task_backlog_duplicate_detection():
    refl = Reflector()
    tasks = [
        {"id": 1, "description": "dup", "component": "c", "dependencies": [], "priority": 1, "status": "pending"},
        {"id": 2, "description": "unique", "component": "c", "dependencies": [], "priority": 2, "status": "done"},
        {"id": 3, "description": "dup", "component": "c", "dependencies": [], "priority": 1, "status": "pending"},
    ]
    analysis = refl._analyze_task_backlog(tasks)
    assert analysis["pending_tasks"] == 2
    assert analysis["done_tasks"] == 1
    assert len(analysis["duplicate_tasks"]) == 1


def test_decision_branches():
    refl = Reflector()
    tasks = [
        {"id": i, "description": f"refactor {i}", "component": "c", "dependencies": [], "priority": 3, "status": "pending"}
        for i in range(6)
    ]
    code_metrics = {"needs_attention": True}
    refactor_decisions = refl._decide_refactoring_priorities(code_metrics, tasks)
    assert refactor_decisions and refactor_decisions[0]["type"] == "refactor_consolidation"

    backlog = {"pending_tasks": 21}
    proc = refl._decide_process_improvements(backlog, {})
    assert proc and proc[0]["type"] == "process_improvement"

    debt = refl._decide_technical_debt_priorities({}, {"duplicate_tasks": [{"description": "d", "task_ids": [1, 2]}]})
    assert debt and debt[0]["type"] == "task_cleanup"


def test_create_debt_task_description():
    refl = Reflector()
    decision = {"type": "task_cleanup", "reason": "Duplicate tasks detected", "duplicates": [{"description": "d", "task_ids": [1, 2]}]}
    task = refl._create_debt_task(decision, 99)
    assert task["description"].startswith("Clean up 1 duplicate tasks")


def test_run_cycle_uses_metrics_provider(tmp_path):
    class DummyProvider:
        def __init__(self):
            self.called = False

        def collect(self):
            self.called = True
            return {"dummy": 1}

    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(
        "- id: 1\n"
        "  description: base\n"
        "  component: core\n"
        "  dependencies: []\n"
        "  priority: 1\n"
        "  status: pending\n"
    )
    code_file = tmp_path / "code.py"
    code_file.write_text("def foo():\n    return 1\n")
    provider = DummyProvider()
    refl = Reflector(tasks_path=tasks_file, analysis_paths=[code_file], metrics_provider=provider)
    tasks = yaml.safe_load(tasks_file.read_text())
    refl.run_cycle(tasks)
    assert provider.called

