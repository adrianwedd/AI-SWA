from __future__ import annotations

import asyncio
import os
import sqlite3
import json
from pathlib import Path

import grpc
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from core.telemetry import setup_telemetry
except Exception:  # pragma: no cover - optional dependency
    FastAPIInstrumentor = None
    setup_telemetry = None

from . import metrics as mp_metrics

from core import plugin_marketplace_pb2 as pb2
from core import plugin_marketplace_pb2_grpc as pb2_grpc

DB_PATH = os.getenv("PLUGIN_DB", "plugins.db")
PLUGIN_DIR = os.getenv("PLUGIN_DIR", "plugin_repo")
GRPC_PORT = os.getenv("GRPC_PORT", "50052")

app = FastAPI()
_grpc_server: grpc.aio.Server | None = None
_metrics_server = None

if setup_telemetry:
    _metrics_server, _ = setup_telemetry(
        service_name="plugin_marketplace",
        metrics_port=int(os.getenv("METRICS_PORT", "0")),
    )
if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS plugins (id TEXT PRIMARY KEY, name TEXT, version TEXT, dependencies TEXT, path TEXT)"
    )
    conn.commit()
    conn.close()


def add_plugin(id: str, name: str, version: str, dependencies: list[str], path: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO plugins (id, name, version, dependencies, path) VALUES (?, ?, ?, ?, ?)",
        (id, name, version, json.dumps(dependencies), path),
    )
    conn.commit()
    conn.close()


def list_plugins_from_db() -> list[dict[str, str]]:
    conn = get_db()
    rows = conn.execute("SELECT id, name, version, dependencies, path FROM plugins").fetchall()
    conn.close()
    return [dict(row) for row in rows]


class MarketplaceServicer(pb2_grpc.PluginMarketplaceServicer):
    async def ListPlugins(self, request: pb2.Empty, context: grpc.aio.ServicerContext) -> pb2.PluginList:
        plugins = [
            pb2.PluginInfo(id=p["id"], name=p["name"], version=p["version"])
            for p in list_plugins_from_db()
        ]
        return pb2.PluginList(plugins=plugins)

    async def DownloadPlugin(
        self, request: pb2.PluginRequest, context: grpc.aio.ServicerContext
    ) -> pb2.PluginData:
        conn = get_db()
        row = conn.execute("SELECT path FROM plugins WHERE id=?", (request.id,)).fetchone()
        conn.close()
        if not row:
            if mp_metrics.ERRORS:
                mp_metrics.ERRORS.add(1, {"plugin_id": request.id})
            context.abort(grpc.StatusCode.NOT_FOUND, "Not found")
        file_path = Path(PLUGIN_DIR) / row["path"]
        try:
            data = file_path.read_bytes()
        except FileNotFoundError:
            if mp_metrics.ERRORS:
                mp_metrics.ERRORS.add(1, {"plugin_id": request.id})
            context.abort(grpc.StatusCode.NOT_FOUND, "Not found")
        if mp_metrics.DOWNLOADS:
            mp_metrics.DOWNLOADS.add(1, {"plugin_id": request.id})
        return pb2.PluginData(data=data)


async def start_grpc() -> None:
    global _grpc_server
    _grpc_server = grpc.aio.server()
    pb2_grpc.add_PluginMarketplaceServicer_to_server(MarketplaceServicer(), _grpc_server)
    _grpc_server.add_insecure_port(f"[::]:{GRPC_PORT}")
    await _grpc_server.start()
    asyncio.create_task(_grpc_server.wait_for_termination())


@app.on_event("startup")
async def _startup() -> None:
    init_db()
    Path(PLUGIN_DIR).mkdir(exist_ok=True)
    await start_grpc()


@app.on_event("shutdown")
async def _shutdown() -> None:
    if _grpc_server:
        await _grpc_server.stop(0)
    if _metrics_server:
        _metrics_server.shutdown()


@app.get("/plugins")
def list_plugins() -> list[dict[str, str]]:
    records = list_plugins_from_db()
    return [
        {"id": r["id"], "name": r["name"], "version": r["version"]}
        for r in records
    ]


@app.get("/plugins/{plugin_id}/download")
def download_plugin(plugin_id: str):
    conn = get_db()
    row = conn.execute("SELECT path FROM plugins WHERE id=?", (plugin_id,)).fetchone()
    conn.close()
    if not row:
        if mp_metrics.ERRORS:
            mp_metrics.ERRORS.add(1, {"plugin_id": plugin_id})
        raise HTTPException(status_code=404, detail="Plugin not found")
    file_path = Path(PLUGIN_DIR) / row["path"]
    if not file_path.exists():
        if mp_metrics.ERRORS:
            mp_metrics.ERRORS.add(1, {"plugin_id": plugin_id})
        raise HTTPException(status_code=404, detail="File not found")
    if mp_metrics.DOWNLOADS:
        mp_metrics.DOWNLOADS.add(1, {"plugin_id": plugin_id})
    return FileResponse(file_path, media_type="application/zip", filename=row["path"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
