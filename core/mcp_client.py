from __future__ import annotations

import httpx
from .config import load_config


def _base_url(host: str | None, port: int | None) -> str:
    cfg = load_config()
    host = host or cfg.get("mcp", {}).get("host", "localhost")
    port = port or cfg.get("mcp", {}).get("port", 8004)
    return f"http://{host}:{int(port)}"


def list_tools(host: str | None = None, port: int | None = None) -> list[dict]:
    """Return available tools from the MCP server."""
    url = f"{_base_url(host, port)}/mcp"
    resp = httpx.post(url, json={"id": 1, "method": "tools/list"}, timeout=5)
    resp.raise_for_status()
    return resp.json()["result"]["tools"]


def call_tool(name: str, host: str | None = None, port: int | None = None) -> str:
    """Execute a tool by name via the MCP server and return stdout."""
    payload = {"id": 1, "method": "tools/call", "params": {"name": name}}
    url = f"{_base_url(host, port)}/mcp"
    resp = httpx.post(url, json=payload, timeout=5)
    resp.raise_for_status()
    return resp.json()["result"]["content"][0]["text"]
