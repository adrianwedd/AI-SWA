"""Task broker API backed by SQLite.

The service exposes a minimal REST interface for managing tasks and their
execution results:

* ``POST /tasks`` creates a new task entry.
* ``GET /tasks`` lists all tasks.
* ``GET /tasks/{id}`` retrieves a single task.
* ``POST /tasks/{id}/result`` stores stdout, stderr and exit code.

All data is persisted in a SQLite database specified by ``DB_PATH``. Two tables
are created on startup: ``tasks`` for task metadata and ``task_results`` for
worker output.
"""

import logging
import os
import sqlite3
import sentry_sdk
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Any
try:
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from core.telemetry import setup_telemetry
except Exception:  # pragma: no cover - optional dependency
    FastAPIInstrumentor = None
    setup_telemetry = None
from core.security import verify_api_key, verify_token, require_role, User
from config import load_config
from core.log_utils import configure_logging
from .queue import publish_task

config = load_config()
DB_PATH = config["broker"]["db_path"]
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI()
if setup_telemetry:
    setup_telemetry(service_name="broker", metrics_port=int(config["broker"]["metrics_port"]))
if FastAPIInstrumentor:
    FastAPIInstrumentor.instrument_app(app)


class AuthMiddleware(BaseHTTPMiddleware):
    """Validate API key and bearer token for all requests."""

    async def dispatch(self, request: Request, call_next):
        try:
            verify_api_key(request.headers.get("X-API-Key"))
            user = verify_token(request.headers.get("Authorization"))
            request.state.user = user
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        return await call_next(request)


app.add_middleware(AuthMiddleware)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, description TEXT, status TEXT, command TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS task_results (task_id INTEGER, stdout TEXT, stderr TEXT, exit_code INTEGER)"
    )
    conn.commit()
    conn.close()


class Task(BaseModel):
    id: int | None = None
    description: str
    status: str = "pending"
    command: str | None = None
    metadata: dict[str, Any] | None = None


class TaskResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int


init_db()


@app.post("/tasks", response_model=Task)
def create_task(
    task: Task,
    __: User = Depends(require_role(["admin"])),
):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tasks (description, status, command) VALUES (?, ?, ?)",
        (task.description, task.status, task.command),
    )
    conn.commit()
    task.id = cur.lastrowid
    conn.close()
    try:
        publish_task(task.id)
    except Exception:  # pragma: no cover - queue optional
        logger.warning("Failed to publish task %s to queue", task.id)
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    __: User = Depends(require_role(["admin", "worker"])),
):
    conn = get_db()
    cur = conn.execute("SELECT id, description, status, command FROM tasks")
    tasks = [
        Task(
            id=row["id"],
            description=row["description"],
            status=row["status"],
            command=row["command"],
        )
        for row in cur.fetchall()
    ]
    conn.close()
    return tasks


@app.get("/tasks/next", response_model=Task | None)
def next_task(__: User = Depends(require_role(["admin", "worker"]))):
    """Atomically pop the next pending task from the queue."""
    conn = get_db()
    conn.isolation_level = None
    conn.execute("BEGIN IMMEDIATE")
    row = conn.execute(
        "SELECT id, description, command FROM tasks WHERE status='pending' ORDER BY id LIMIT 1"
    ).fetchone()
    if not row:
        conn.execute("COMMIT")
        conn.close()
        return None
    task_id = row["id"]
    conn.execute(
        "UPDATE tasks SET status='in_progress' WHERE id=? AND status='pending'",
        (task_id,),
    )
    conn.execute("COMMIT")
    conn.close()
    return Task(id=task_id, description=row["description"], status="in_progress", command=row["command"])


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    __: User = Depends(require_role(["admin", "worker"])),
):
    conn = get_db()
    row = conn.execute(
        "SELECT id, description, status, command FROM tasks WHERE id = ?",
        (task_id,),
    ).fetchone()
    conn.close()
    if row:
        return Task(
            id=row["id"],
            description=row["description"],
            status=row["status"],
            command=row["command"],
        )
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks/{task_id}/result")
def save_result(
    task_id: int,
    result: TaskResult,
    __: User = Depends(require_role(["worker", "admin"])),
):
    conn = get_db()
    exists = conn.execute(
        "SELECT 1 FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not exists:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute(
        "INSERT INTO task_results (task_id, stdout, stderr, exit_code) VALUES (?, ?, ?, ?)",
        (task_id, result.stdout, result.stderr, result.exit_code),
    )
    conn.execute(
        "UPDATE tasks SET status='done' WHERE id = ?",
        (task_id,),
    )
    conn.commit()
    conn.close()
    return {"status": "ok"}
