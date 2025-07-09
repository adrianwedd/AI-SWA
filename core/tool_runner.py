from __future__ import annotations

import shlex
import subprocess
from pathlib import Path
from typing import Sequence


class ToolRunner:
    """Execute shell commands within a sandbox."""

    def __init__(self, sandbox_root: str | Path, allowed_commands: Sequence[str] | None = None) -> None:
        self.sandbox_root = Path(sandbox_root).resolve()
        self.allowed_commands = set(allowed_commands or [])
        self.sandbox_root.mkdir(parents=True, exist_ok=True)

    def _validate_args(self, args: Sequence[str]) -> None:
        if self.allowed_commands and args[0] not in self.allowed_commands:
            raise PermissionError(f"Command {args[0]} is not allowed")
        for arg in args[1:]:
            p = Path(arg)
            if p.is_absolute() or ".." in p.parts:
                raise PermissionError("Absolute paths and parent references are not allowed")

    def run(self, command: str | Sequence[str]) -> subprocess.CompletedProcess:
        """Run ``command`` inside the sandbox and return the result."""
        args = shlex.split(command) if isinstance(command, str) else list(command)
        if not args:
            raise ValueError("No command provided")
        self._validate_args(args)
        return subprocess.run(args, cwd=self.sandbox_root, capture_output=True, text=True)

