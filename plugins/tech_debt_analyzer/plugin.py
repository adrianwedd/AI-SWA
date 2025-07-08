from pathlib import Path
from core.self_auditor import SelfAuditor


def run(target: str = "core") -> None:
    """Analyze code complexity in ``target`` directory and print results."""
    auditor = SelfAuditor(complexity_threshold=10)
    paths = [p for p in Path(target).rglob("*.py")]
    metrics = auditor.analyze(paths)
    print(metrics)
