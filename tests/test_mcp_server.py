import json
import os
from importlib import reload
from pathlib import Path

from fastapi.testclient import TestClient


def setup_module(module):
    tmp = Path(module.__file__).parent / "mcp_plugins"
    tmp.mkdir(exist_ok=True)
    plugin = tmp / "demo"
    plugin.mkdir(exist_ok=True)
    (plugin / "plugin.py").write_text("print('hello')")
    manifest = {
        "id": "demo",
        "name": "Demo",
        "version": "0.1.0",
        "permissions": ["read_files"],
    }
    (plugin / "manifest.json").write_text(json.dumps(manifest))
    os.environ["MCP_PLUGIN_DIR"] = str(tmp)
    global svc
    import services.mcp_server as svc_mod
    svc = reload(svc_mod)


def teardown_module(module):
    os.environ.pop("MCP_PLUGIN_DIR")
    tmp = Path(module.__file__).parent / "mcp_plugins"
    if tmp.exists():
        for item in tmp.iterdir():
            if item.is_dir():
                for f in item.iterdir():
                    f.unlink()
                item.rmdir()
        tmp.rmdir()


def test_list_and_call():
    client = TestClient(svc.app)

    resp = client.post("/mcp", json={"id": 1, "method": "tools/list"})
    assert resp.status_code == 200
    tools = resp.json()["result"]["tools"]
    assert any(t["name"] == "demo" for t in tools)

    resp = client.post("/mcp", json={"id": 2, "method": "tools/call", "params": {"name": "demo"}})
    assert resp.status_code == 200
    data = resp.json()["result"]["content"][0]["text"].strip()
    assert data == "hello"
