
"""Simple API Gateway routing to internal services."""

from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from core.telemetry import setup_telemetry
except Exception:  # pragma: no cover - optional dependency
    FastAPIInstrumentor = None
    setup_telemetry = None

app = FastAPI()

if setup_telemetry:
    setup_telemetry(
        service_name="api_gateway",
        metrics_port=int(os.getenv("METRICS_PORT", "0")),
        jaeger_endpoint=os.getenv("JAEGER_ENDPOINT"),
    )
if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)

BROKER_URL = os.getenv("BROKER_URL", "http://broker:8000")
ORCH_URL = os.getenv("ORCH_URL", "http://orchestrator-api:8002")


async def _proxy(request: Request, target: str) -> Response:
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                request.method,
                target,
                content=await request.body(),
                headers=request.headers.raw,
            )
        except httpx.RequestError as exc:
            return JSONResponse(status_code=502, content={"error": str(exc)})
    return Response(content=resp.content, status_code=resp.status_code, headers=resp.headers)


@app.api_route("/tasks{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def tasks_proxy(request: Request, path: str = ""):
    return await _proxy(request, f"{BROKER_URL}/tasks{path}")


@app.api_route("/orchestrator{path:path}", methods=["GET", "POST"])
async def orch_proxy(request: Request, path: str = ""):
    return await _proxy(request, f"{ORCH_URL}{path}")
