from __future__ import annotations

import shutil
import subprocess
import shlex
from pathlib import Path

from config import load_config
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


def _docker_available() -> bool:
    """Return ``True`` if Docker is installed and the daemon is reachable."""
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run(
            [docker, "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


def run_plugin_container(plugin_dir: str | Path, image: str = "plugin-sandbox") -> subprocess.CompletedProcess:
    """Execute ``plugin.py`` inside the Docker sandbox.

    This builds the sandbox image if necessary and runs the plugin with
    ``--network none`` and a read-only filesystem. A ``tmpfs`` is mounted at
    ``/tmp`` for temporary write access.
    """

    if not _docker_available():
        raise EnvironmentError("Docker is not available")

    plugin_path = Path(plugin_dir).resolve()
    manifest = load_manifest(plugin_path / "manifest.json")

    root = Path(__file__).resolve().parents[1]
    dockerfile = root / "plugins" / "sandbox" / "Dockerfile"

    build_cmd = [
        "docker",
        "build",
        "-t",
        image,
        "-f",
        str(dockerfile),
        str(root),
    ]
    subprocess.run(build_cmd, check=True)

    run_cmd = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--tmpfs",
        "/tmp",
        "-v",
        f"{plugin_path}:/plugin:ro",
        image,
        "python",
        "-I",
        "/plugin/plugin.py",
    ]
    return subprocess.run(run_cmd, capture_output=True, text=True)

