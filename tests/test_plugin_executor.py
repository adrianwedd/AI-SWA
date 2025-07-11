import json
from pathlib import Path

import pytest

from plugins.executor import run_plugin


def _create_plugin(tmp_path: Path, pid: str, perms: list[str]) -> Path:
    pdir = tmp_path / pid
    pdir.mkdir()
    (pdir / "plugin.py").write_text("print('ok')")
    manifest = {
        "id": pid,
        "name": pid,
        "version": "0.1",
        "permissions": perms,
    }
    (pdir / "manifest.json").write_text(json.dumps(manifest))
    return pdir


def test_run_plugin(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGIN_POLICY_FILE", str(tmp_path / "policy.json"))
    (tmp_path / "policy.json").write_text(json.dumps({"plugins": {"demo": {"permissions": ["read_files"]}}}))
    plugin_dir = _create_plugin(tmp_path, "demo", ["read_files"])
    result = run_plugin(plugin_dir)
    assert result.stdout.strip() == "ok"


def test_run_plugin_disallowed(tmp_path, monkeypatch):
    monkeypatch.setenv("PLUGIN_POLICY_FILE", str(tmp_path / "policy.json"))
    (tmp_path / "policy.json").write_text(json.dumps({"plugins": {}}))
    plugin_dir = _create_plugin(tmp_path, "demo", ["read_files"])
    with pytest.raises(ValueError):
        run_plugin(plugin_dir)
