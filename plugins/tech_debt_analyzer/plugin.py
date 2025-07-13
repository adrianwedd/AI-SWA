from pathlib import Path
import logging

from core.self_auditor import SelfAuditor
from core.log_utils import configure_logging


def run(target: str = "core") -> None:
    """Analyze code complexity in ``target`` directory and print results."""
    configure_logging()
    auditor = SelfAuditor(complexity_threshold=10)
    paths = [p for p in Path(target).rglob("*.py")]
    metrics = auditor.analyze(paths)
    logging.info(str(metrics))
