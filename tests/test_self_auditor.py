import os

from core.self_auditor import SelfAuditor  # noqa: E402


def test_self_auditor_audit(tmp_path):
    pyfile = tmp_path / "sample.py"
    pyfile.write_text(
        "def foo(x):\n    if x > 1:\n        return 1\n    else:\n        return 0\n"
    )
    auditor = SelfAuditor(complexity_threshold=1)

    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        new_tasks = auditor.audit([])
    finally:
        os.chdir(cwd)

    assert new_tasks
    assert new_tasks[0]["metadata"]["type"] == "refactor"


def test_self_auditor_analyze(tmp_path):
    target = tmp_path / "sample.py"
    target.write_text("def foo():\n    return 1\n")
    auditor = SelfAuditor()
    metrics = auditor.analyze([target])
    key = str(target)
    assert key in metrics
    assert metrics[key]["maintainability"]["mi"] > 0


def test_self_auditor_wily_history(tmp_path):
    """Ensure wily metrics are incorporated when enabled."""
    import subprocess

    repo = tmp_path
    subprocess.run(["git", "init"], cwd=repo)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=repo)
    subprocess.run(["git", "config", "user.name", "Tester"], cwd=repo)

    sample = repo / "sample.py"
    sample.write_text("def foo(x):\n    return x\n")
    subprocess.run(["git", "add", "sample.py"], cwd=repo)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo)

    sample.write_text(
        "def foo(x):\n    if x > 1:\n        return 1\n    else:\n        return 0\n"
    )
    subprocess.run(["git", "add", "sample.py"], cwd=repo)
    subprocess.run(["git", "commit", "-m", "update"], cwd=repo)

    auditor = SelfAuditor(complexity_threshold=1, use_wily=True)

    cwd = os.getcwd()
    os.chdir(repo)
    try:
        tasks = auditor.audit([])
    finally:
        os.chdir(cwd)

    assert tasks
    meta = tasks[0]["metadata"]
    assert "delta_complexity" in meta
    assert meta["delta_complexity"] != 0


def test_self_auditor_class_nodes(tmp_path):
    pyfile = tmp_path / "cls.py"
    pyfile.write_text(
        "class Foo:\n    def bar(self):\n        if True:\n            return 1\n        return 0\n"
    )
    auditor = SelfAuditor(complexity_threshold=1)
    metrics = auditor.analyze([pyfile])
    key = str(pyfile)
    assert key in metrics
    data = metrics[key]
    types = {item["type"] for item in data["complexity"]}
    assert "class" in types
