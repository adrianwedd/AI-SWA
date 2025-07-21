from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException

from core.plugins import load_manifest
from plugins.executor import run_plugin

PLUGIN_DIR = Path(os.getenv("MCP_PLUGIN_DIR", "plugins"))

app = FastAPI()


def _list_tools() -> dict[str, Any]:
    tools = []
    for manifest_path in PLUGIN_DIR.glob("*/manifest.json"):
        try:
            manifest = load_manifest(manifest_path)
        except Exception:
            continue
        tools.append({"name": manifest.id, "title": manifest.name, "description": manifest.name})
    return {"tools": tools}


def _call_tool(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="name required")
    plugin_dir = PLUGIN_DIR / name
    if not plugin_dir.exists():
        raise HTTPException(status_code=404, detail="plugin not found")
    result = run_plugin(plugin_dir)
    return {"content": [{"type": "text", "text": result.stdout}]} 


@app.post("/mcp")
def handle(request: dict) -> dict:
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")

    if method == "tools/list":
        result = _list_tools()
    elif method == "tools/call":
        result = _call_tool(params)
    else:
        raise HTTPException(status_code=400, detail="unknown method")

    return {"id": req_id, "result": result}
