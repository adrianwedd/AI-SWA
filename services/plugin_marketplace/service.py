from __future__ import annotations

import asyncio
import os
import sqlite3
import json
from pathlib import Path

import grpc
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import signal
from config import load_config, reload_config

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.grpc import GrpcInstrumentorServer
    from core.telemetry import setup_telemetry
except Exception:  # pragma: no cover - optional dependency
    FastAPIInstrumentor = None
    GrpcInstrumentorServer = None
    setup_telemetry = None

from . import metrics as mp_metrics
from . import analytics

from core import plugin_marketplace_pb2 as pb2
from core import plugin_marketplace_pb2_grpc as pb2_grpc

DB_PATH = os.getenv("PLUGIN_DB", "plugins.db")
PLUGIN_DIR = os.getenv("PLUGIN_DIR", "plugin_repo")
GRPC_PORT = os.getenv("GRPC_PORT", "50052")

app = FastAPI()
_grpc_server: grpc.aio.Server | None = None
_metrics_server = None
config = load_config()

if setup_telemetry:
    _metrics_server, _ = setup_telemetry(
        service_name="plugin_marketplace",
        metrics_port=int(os.getenv("METRICS_PORT", "0")),
        jaeger_endpoint=config["tracing"]["jaeger_endpoint"],
    )
if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)
if GrpcInstrumentorServer:
    GrpcInstrumentorServer().instrument()

def _reload_config(signum, frame) -> None:
    global config
    config = reload_config()

signal.signal(signal.SIGHUP, _reload_config)



def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS plugins (id TEXT PRIMARY KEY, name TEXT, version TEXT, dependencies TEXT, path TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS reviews (plugin_id TEXT, rating INTEGER, review TEXT)"
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


def update_plugin(id: str, name: str, version: str, dependencies: list[str], path: str) -> None:
    """Update an existing plugin or insert if missing."""
    conn = get_db()
    old = conn.execute("SELECT path FROM plugins WHERE id=?", (id,)).fetchone()
    conn.execute(
        "INSERT OR REPLACE INTO plugins (id, name, version, dependencies, path) VALUES (?, ?, ?, ?, ?)",
        (id, name, version, json.dumps(dependencies), path),
    )
    conn.commit()
    conn.close()
    if old and old["path"] != path:
        old_file = Path(PLUGIN_DIR) / old["path"]
        if old_file.exists():
            old_file.unlink()


def remove_plugin(id: str) -> None:
    """Delete a plugin and associated files and reviews."""
    conn = get_db()
    row = conn.execute("SELECT path FROM plugins WHERE id=?", (id,)).fetchone()
    conn.execute("DELETE FROM plugins WHERE id=?", (id,))
    conn.execute("DELETE FROM reviews WHERE plugin_id=?", (id,))
    conn.commit()
    conn.close()
    if row:
        file = Path(PLUGIN_DIR) / row["path"]
        if file.exists():
            file.unlink()


def list_plugins_from_db() -> list[dict[str, str]]:
    conn = get_db()
    rows = conn.execute("SELECT id, name, version, dependencies, path FROM plugins").fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_review(plugin_id: str, rating: int, review: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO reviews (plugin_id, rating, review) VALUES (?, ?, ?)",
        (plugin_id, rating, review),
    )
    conn.commit()
    conn.close()


def list_reviews(plugin_id: str) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT rating, review FROM reviews WHERE plugin_id=?",
        (plugin_id,),
    ).fetchall()
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
        if analytics.DOWNLOADS:
            analytics.DOWNLOADS.inc()
        return pb2.PluginData(data=data)

    async def SubmitReview(
        self, request: pb2.SubmitReviewRequest, context: grpc.aio.ServicerContext
    ) -> pb2.Empty:
        add_review(request.plugin_id, request.rating, request.comment)
        if analytics.RATINGS:
            analytics.RATINGS.inc()
        return pb2.Empty()

    async def ListReviews(
        self, request: pb2.ReviewRequest, context: grpc.aio.ServicerContext
    ) -> pb2.ReviewList:
        rows = list_reviews(request.plugin_id)
        reviews = [pb2.Review(rating=r["rating"], comment=r["review"]) for r in rows]
        return pb2.ReviewList(reviews=reviews)


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
    if analytics.DOWNLOADS:
        analytics.DOWNLOADS.inc()
    return FileResponse(file_path, media_type="application/zip", filename=row["path"])


@app.put("/plugins/{plugin_id}")
def update_plugin_api(plugin_id: str, payload: dict):
    """Update a plugin's metadata and stored archive."""
    name = payload.get("name", plugin_id)
    version = payload.get("version")
    path = payload.get("path")
    deps = payload.get("dependencies", [])
    if not version or not path:
        raise HTTPException(status_code=400, detail="version and path required")
    update_plugin(plugin_id, name, version, deps, path)
    return {"status": "ok"}


@app.delete("/plugins/{plugin_id}")
def delete_plugin_api(plugin_id: str):
    remove_plugin(plugin_id)
    return {"status": "ok"}


@app.post("/plugins/{plugin_id}/reviews")
def submit_review(plugin_id: str, payload: dict):
    rating = int(payload.get("rating", 0))
    comment = str(payload.get("review", ""))
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="rating must be 1-5")
    add_review(plugin_id, rating, comment)
    if analytics.RATINGS:
        analytics.RATINGS.inc()
    return {"status": "ok"}


@app.get("/plugins/{plugin_id}/reviews")
def get_reviews_api(plugin_id: str):
    rows = list_reviews(plugin_id)
    return rows


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8003)
