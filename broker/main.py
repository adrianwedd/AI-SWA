import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = os.environ.get("DB_PATH", "tasks.db")

app = FastAPI()


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


class TaskResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int


init_db()


@app.post("/tasks", response_model=Task)
def create_task(task: Task):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO tasks (description, status, command) VALUES (?, ?, ?)",
        (task.description, task.status, task.command),
    )
    conn.commit()
    task.id = cur.lastrowid
    conn.close()
    return task


@app.get("/tasks", response_model=list[Task])
def list_tasks():
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


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
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
def save_result(task_id: int, result: TaskResult):
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
    conn.commit()
    conn.close()
    return {"status": "ok"}
