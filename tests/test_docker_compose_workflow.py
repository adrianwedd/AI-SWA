import os
import time
import subprocess
import shutil
from pathlib import Path

import pytest
import requests

from core.io_client import ping

COMPOSE_CMD = ["docker", "compose"]


def _compose(args, cwd, **kwargs):
    return subprocess.run(COMPOSE_CMD + args, cwd=cwd, check=True, **kwargs)


@pytest.fixture(scope="module")
def compose_services():
    if shutil.which("docker") is None:
        pytest.skip("Docker not installed")
    root = Path(__file__).resolve().parents[1]
    _compose(["up", "-d", "--build"], cwd=root)
    base_url = "http://localhost:8000"
    for _ in range(30):
        try:
            r = requests.get(f"{base_url}/tasks", timeout=1)
            if r.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.5)
    else:
        _compose(["logs"], cwd=root)
        _compose(["down"], cwd=root)
        raise RuntimeError("Services failed to start")

    for _ in range(20):
        try:
            if ping("ok") == "pong:ok":
                break
        except Exception:
            time.sleep(0.5)
    else:
        _compose(["down"], cwd=root)
        raise RuntimeError("IO service failed to start")

    yield base_url
    _compose(["down"], cwd=root)


def _fetch_result(task_id, cwd):
    cmd = COMPOSE_CMD + [
        "exec",
        "-T",
        "broker",
        "python",
        "-c",
        (
            "import sqlite3, json; "
            "conn=sqlite3.connect('tasks.db'); "
            "row=conn.execute('SELECT stdout, stderr, exit_code FROM task_results "
            f"WHERE task_id={task_id}').fetchone(); "
            "print(json.dumps(row));"
        ),
    ]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def test_compose_workflow(compose_services):
    base_url = compose_services
    resp = requests.post(
        f"{base_url}/tasks",
        json={"description": "demo", "command": "echo compose"},
        timeout=5,
    )
    resp.raise_for_status()
    task_id = resp.json()["id"]

    root = Path(__file__).resolve().parents[1]
    result = None
    for _ in range(20):
        out = _fetch_result(task_id, root)
        if out and out != "None":
            result = out
            break
        time.sleep(0.5)

    assert result is not None
    stdout, stderr, code = eval(result)
    assert stdout.strip() == "compose"
    assert stderr == ""
    assert code == 0
    assert ping("hello") == "pong:hello"
