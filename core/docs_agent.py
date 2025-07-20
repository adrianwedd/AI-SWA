"""SWA-DOCS-01: Documentation verification agent."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path


class DocsAgent:
    """Verify code comments and docstring completeness."""

    def __init__(self, targets: list[str] | None = None, report_dir: Path | str = "docs/reports") -> None:
        self.targets = targets or ["core"]
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    def run_pylint_docstrings(self) -> tuple[Path, float]:
        """Run pylint docstring checks and return log path and coverage."""
        report = self.report_dir / "docstring.log"
        cmd = ["pylint", "--disable=all", "--enable=missing-docstring", *self.targets]
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        out = proc.stdout
        with report.open("w", encoding="utf-8") as fh:
            fh.write(out)
        missing = out.count("missing-module-docstring") + out.count("missing-class-docstring") + out.count("missing-function-docstring")
        coverage = 1.0 / (missing + 1)
        return report, coverage

    # ------------------------------------------------------------------
    def run(self) -> tuple[list[Path], float]:
        """Execute documentation checks and return reports and coverage."""
        self.logger.info("DocsAgent validating comments and docstrings")
        report, coverage = self.run_pylint_docstrings()
        return [report], coverage
