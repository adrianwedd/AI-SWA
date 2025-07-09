import json
import time
import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.plugin_marketplace import service as svc
from services.plugin_marketplace import pipeline


def _start_service(tmp_path: Path):
    """Reload service with temporary database and repo."""
    import os

    os.environ["PLUGIN_DB"] = str(tmp_path / "plugins.db")
    os.environ["PLUGIN_DIR"] = str(tmp_path / "repo")
    os.environ["GRPC_PORT"] = "60060"
    module = importlib.reload(svc)
    module.init_db()
    return module


def _stop_service(module):
    if module._grpc_server:
        module._grpc_server.stop(None)
        time.sleep(0.2)


def _make_plugin(tmp_path: Path, plugin_id: str, fail_scan=False) -> Path:
    plugin_dir = tmp_path / plugin_id
    plugin_dir.mkdir()
    manifest = {
        "id": plugin_id,
        "name": plugin_id.title(),
        "version": "0.1.0",
        "permissions": ["read_files"],
        "dependencies": [],
        "compatibility": ">=0.1",
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
    code = "def run():\n    return 'ok'\n"
    if fail_scan:
        code += "# FAIL_SCAN\n"
    (plugin_dir / "plugin.py").write_text(code)
    return plugin_dir


@pytest.fixture()
def marketplace(tmp_path):
    module = _start_service(tmp_path)
    yield module
    _stop_service(module)


def test_publish_plugin(marketplace, tmp_path):
    plugin = _make_plugin(tmp_path, "demo")
    pipeline.certify_and_publish(plugin)

    client = TestClient(marketplace.app)
    resp = client.get("/plugins")
    assert any(p["id"] == "demo" for p in resp.json())


def test_scan_failure_blocks_publication(marketplace, tmp_path):
    plugin = _make_plugin(tmp_path, "bad", fail_scan=True)
    with pytest.raises(pipeline.ScanError):
        pipeline.certify_and_publish(plugin)

    client = TestClient(marketplace.app)
    resp = client.get("/plugins")
    assert all(p["id"] != "bad" for p in resp.json())
