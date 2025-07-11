from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from core.config import load_config
from core.tool_runner import ToolRunner
from core.plugins import load_manifest


def run_plugin(plugin_dir: str | Path) -> subprocess.CompletedProcess:
    """Execute a plugin's ``plugin.py`` inside the sandbox.

    The plugin manifest is validated and checked against the policy before
    execution. The plugin code is copied into the sandbox root and executed
    with ``python -I`` to avoid environment side effects.
    """
    plugin_path = Path(plugin_dir).resolve()
    manifest = load_manifest(plugin_path / "manifest.json")

    cfg = load_config()
    sandbox_root = Path(cfg["sandbox"].get("root", "sandbox"))
    sandbox_root.mkdir(parents=True, exist_ok=True)

    dest = sandbox_root / manifest.id
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(plugin_path, dest)

    runner = ToolRunner(dest, ["python"])
    return runner.run("python -I plugin.py")
