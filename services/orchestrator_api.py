"""REST API to control the Orchestrator."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from core.config import load_config
from core.security import verify_api_key, require_role, User
from core.telemetry import setup_telemetry

app = FastAPI()
config = load_config()
setup_telemetry(
    service_name="orchestrator_api",
    metrics_port=0,
    jaeger_endpoint=config["tracing"]["jaeger_endpoint"],
)
FastAPIInstrumentor.instrument_app(app)

_proc: Optional[subprocess.Popen] = None


def _is_running() -> bool:
    return _proc is not None and _proc.poll() is None


@app.post("/start")
def start_orchestrator(
    _: None = Depends(verify_api_key),
    __: User = Depends(require_role(["admin"])),
):
    """Start the orchestrator subprocess."""
    global _proc
    if _is_running():
        raise HTTPException(status_code=400, detail="Already running")
    cmd = [sys.executable, "-m", "ai_swa.orchestrator", "_run", "--config", "config.yaml"]
    env = os.environ.copy()
    env.setdefault("PYTHONPATH", str(os.getcwd()))
    _proc = subprocess.Popen(cmd, env=env)
    return {"pid": _proc.pid}


@app.post("/stop")
def stop_orchestrator(
    _: None = Depends(verify_api_key),
    __: User = Depends(require_role(["admin"])),
):
    """Terminate the orchestrator subprocess."""
    global _proc
    if not _is_running():
        raise HTTPException(status_code=400, detail="Not running")
    os.kill(_proc.pid, signal.SIGTERM)
    try:
        _proc.wait(timeout=5)
    finally:
        pid = _proc.pid
        _proc = None
    return {"pid": pid}


@app.get("/status")
def status(_: None = Depends(verify_api_key)):
    """Return whether the orchestrator is running."""
    if _is_running():
        return {"running": True, "pid": _proc.pid}
    return {"running": False}

