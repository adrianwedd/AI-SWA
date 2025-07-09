import importlib
import json
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from services.plugin_marketplace import service as svc
from services.plugin_marketplace import pipeline


def _start_service(tmp_path: Path):
    import os
    os.environ["PLUGIN_DB"] = str(tmp_path / "plugins.db")
    os.environ["PLUGIN_DIR"] = str(tmp_path / "repo")
    os.environ["GRPC_PORT"] = "60061"
    module = importlib.reload(svc)
    module.init_db()
    return module


def _stop_service(module):
    if module._grpc_server:
        module._grpc_server.stop(None)
        time.sleep(0.2)


def _make_plugin(tmp_path: Path, plugin_id: str, version: str) -> Path:
    plugin_dir = tmp_path / f"{plugin_id}_{version}"
    plugin_dir.mkdir()
    manifest = {
        "id": plugin_id,
        "name": plugin_id.title(),
        "version": version,
        "permissions": ["read_files"],
        "dependencies": [],
        "compatibility": ">=0.1",
    }
    (plugin_dir / "manifest.json").write_text(json.dumps(manifest))
    (plugin_dir / "plugin.py").write_text("def run():\n    return 'ok'\n")
    return plugin_dir


@pytest.fixture()
def marketplace(tmp_path):
    module = _start_service(tmp_path)
    yield module
    _stop_service(module)


def test_update_and_remove_plugin(marketplace, tmp_path):
    first = _make_plugin(tmp_path, "demo", "0.1.0")
    pipeline.certify_and_publish(first)

    client = TestClient(marketplace.app)
    resp = client.get("/plugins")
    assert any(p["version"] == "0.1.0" for p in resp.json() if p["id"] == "demo")

    updated = _make_plugin(tmp_path, "demo", "0.2.0")
    pipeline.certify_and_publish(updated)

    resp = client.get("/plugins")
    assert any(p["version"] == "0.2.0" for p in resp.json() if p["id"] == "demo")
    files = list((tmp_path / "repo").iterdir())
    assert len(files) == 1 and "0.2.0" in files[0].name

    svc.remove_plugin("demo")
    resp = client.get("/plugins")
    assert all(p["id"] != "demo" for p in resp.json())
    assert not any((tmp_path / "repo").iterdir())
