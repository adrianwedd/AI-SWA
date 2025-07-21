from __future__ import annotations

"""Registry for approved CLI tools with confirmation checks."""

import builtins
import json
import shlex
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path

from .config import load_config


@dataclass
class Tool:
    """Metadata for a command line tool."""

    command: str
    description: str = ""
    confirmed: bool = False


class ToolRegistry:
    """Manage approved CLI tools and enforce confirmation."""

    def __init__(self, path: str | Path | None = None) -> None:
        cfg = load_config()
        sec = cfg.get("security", {})
        default_path = Path(sec.get("tool_registry_file", "plugins/tool_registry.json"))
        self.path = Path(path or default_path)
        self.tools: dict[str, Tool] = {}
        self._orig_open = builtins.open
        self._orig_run = subprocess.run
        if self.path.exists():
            self._load()

    # internal helper using original open to avoid hooks
    def _load(self) -> None:
        with self._orig_open(self.path, "r") as fh:
            data = json.load(fh)
        for cmd, info in data.get("tools", {}).items():
            self.tools[cmd] = Tool(**info)

    def _save(self) -> None:
        data = {"tools": {cmd: asdict(tool) for cmd, tool in self.tools.items()}}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._orig_open(self.path, "w") as fh:
            json.dump(data, fh, indent=2)

    def register(self, command: str, description: str = "") -> None:
        if command not in self.tools:
            self.tools[command] = Tool(command, description)
            self._save()

    def confirm(self, command: str) -> None:
        tool = self.tools.get(command)
        if not tool:
            raise KeyError(command)
        if not tool.confirmed:
            tool.confirmed = True
            self._save()

    def require(self, command: str) -> None:
        tool = self.tools.get(command)
        if not tool:
            raise PermissionError(f"Tool '{command}' is not registered")
        if not tool.confirmed:
            raise PermissionError(f"Tool '{command}' is not confirmed")

    def hook_subprocess(self) -> None:
        """Patch ``subprocess.run`` to enforce registry checks."""

        def _run(args, *a, **k):
            cmd = shlex.split(args)[0] if isinstance(args, str) else args[0]
            self.require(cmd)
            return self._orig_run(args, *a, **k)

        subprocess.run = _run

    def unhook_subprocess(self) -> None:
        subprocess.run = self._orig_run

    def hook_filesystem(self) -> None:
        """Patch ``open`` to enforce registry checks for file access."""

        def _open(file, mode="r", *a, **k):
            self.require("open")
            return self._orig_open(file, mode, *a, **k)

        builtins.open = _open

    def unhook_filesystem(self) -> None:
        builtins.open = self._orig_open

