"""SWA-QA-01: Static analysis and security scanning agent."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path


class QAAgent:
    """Run static analysis tools like Bandit and Pylint."""

    def __init__(self, targets: list[str] | None = None, report_dir: Path | str = "docs/reports") -> None:
        self.targets = targets or ["core"]
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    def run_bandit(self) -> Path:
        """Execute Bandit against ``self.targets`` and return report path."""
        report = self.report_dir / "bandit.json"
        cmd = ["bandit", "-r", *self.targets, "-x", "tests", "-f", "json", "-o", str(report)]
        subprocess.run(cmd, check=False)
        return report

    # ------------------------------------------------------------------
    def run_pylint(self) -> Path:
        """Run pylint on ``self.targets`` and return log file path."""
        report = self.report_dir / "pylint.log"
        with report.open("w") as fh:
            subprocess.run(["pylint", *self.targets], stdout=fh, stderr=subprocess.STDOUT, check=False)
        return report

    # ------------------------------------------------------------------
    def run(self) -> list[Path]:
        """Run all QA checks and return list of generated reports."""
        self.logger.info("QAAgent running static analysis")
        reports = [self.run_bandit(), self.run_pylint()]
        return reports
