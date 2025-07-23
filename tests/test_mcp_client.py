import os
import sys
import time
import json
import subprocess
from pathlib import Path

import requests

from core import mcp_client


def start_server(tmp_path: Path, port: int) -> subprocess.Popen:
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    demo = plugin_dir / "demo"
    demo.mkdir()
    (demo / "plugin.py").write_text("print('hello')")
    manifest = {"id": "demo", "name": "Demo", "version": "0.1.0", "permissions": ["read_files"]}
    (demo / "manifest.json").write_text(json.dumps(manifest))
    env = os.environ.copy()
    env["MCP_PLUGIN_DIR"] = str(plugin_dir)
    proc = subprocess.Popen([
        sys.executable,
        "-m",
        "uvicorn",
        "services.mcp_server:app",
        "--port",
        str(port),
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    url = f"http://localhost:{port}/mcp"
    for _ in range(20):
        try:
            requests.post(url, json={"id":0,"method":"tools/list"}, timeout=1)
            break
        except requests.RequestException:
            time.sleep(0.2)
    return proc


def test_client_list_and_call(tmp_path):
    port = 61000
    proc = start_server(tmp_path, port)
    try:
        tools = mcp_client.list_tools(host="localhost", port=port)
        assert any(t["name"] == "demo" for t in tools)
        out = mcp_client.call_tool("demo", host="localhost", port=port)
        assert out.strip() == "hello"
    finally:
        proc.terminate()
        proc.wait(timeout=5)
