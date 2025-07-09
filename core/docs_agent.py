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
    def run_pylint_docstrings(self) -> Path:
        """Run pylint docstring checks and return log path."""
        report = self.report_dir / "docstring.log"
        cmd = ["pylint", "--disable=all", "--enable=missing-docstring", *self.targets]
        with report.open("w") as fh:
            subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, check=False)
        return report

    # ------------------------------------------------------------------
    def run(self) -> list[Path]:
        """Execute documentation checks."""
        self.logger.info("DocsAgent validating comments and docstrings")
        return [self.run_pylint_docstrings()]
