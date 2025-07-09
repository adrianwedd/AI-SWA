"""SWA-SUPER-01: Simple supervisor dispatching specialized agents."""

from __future__ import annotations

import logging
import re
import subprocess

from .qa_agent import QAAgent
from .docs_agent import DocsAgent


class Supervisor:
    """Activate QA or Docs agents based on commit labels."""

    def __init__(self, qa_agent: QAAgent | None = None, docs_agent: DocsAgent | None = None) -> None:
        self.qa_agent = qa_agent or QAAgent()
        self.docs_agent = docs_agent or DocsAgent()
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    def _last_commit_message(self) -> str:
        result = subprocess.run([
            "git",
            "log",
            "-1",
            "--pretty=%B",
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
        return result.stdout.strip()

    # ------------------------------------------------------------------
    def _parse_label(self, message: str) -> str:
        match = re.match(r"(\w+)\(", message)
        return match.group(1) if match else ""

    # ------------------------------------------------------------------
    def run(self, commit_message: str | None = None) -> None:
        """Run agents based on ``commit_message`` or last git commit."""
        message = commit_message or self._last_commit_message()
        label = self._parse_label(message)
        self.logger.info("Supervisor handling label: %s", label)
        if label == "bug":
            self.logger.info("Triggering QAAgent")
            self.qa_agent.run()
        if label == "docs":
            self.logger.info("Triggering DocsAgent")
            self.docs_agent.run()
