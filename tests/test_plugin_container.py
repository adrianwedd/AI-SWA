import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from plugins.executor import run_plugin_container


def _docker_ready() -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run([docker, "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _docker_ready(), reason="Docker not available")
def test_run_plugin_container(tmp_path):
    plugin_dir = tmp_path / "demo"
    plugin_dir.mkdir()
    (plugin_dir / "plugin.py").write_text("print('ok')")
    manifest = {
        "id": "demo",
        "name": "Demo",
        "version": "0.1",
        "permissions": ["read_files"],
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))

    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"plugins": {"demo": {"permissions": ["read_files"]}}}))
    os.environ["PLUGIN_POLICY_FILE"] = str(policy)

    result = run_plugin_container(plugin_dir)
    assert result.stdout.strip() == "ok"
