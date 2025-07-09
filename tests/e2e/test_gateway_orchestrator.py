import subprocess
import shutil
import time
from pathlib import Path

import pytest
import requests

COMPOSE_CMD = ["docker", "compose"]


def _compose(args, cwd, **kwargs):
    return subprocess.run(COMPOSE_CMD + args, cwd=cwd, check=True, **kwargs)


@pytest.fixture(scope="module")
def compose_stack():
    if shutil.which("docker") is None:
        pytest.skip("Docker not installed")
    root = Path(__file__).resolve().parents[2]
    _compose(["up", "-d", "--build"], cwd=root)
    base_url = "http://localhost:8080"
    for _ in range(40):
        try:
            r = requests.get(f"{base_url}/tasks", timeout=1)
            if r.status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.5)
    else:
        logs = subprocess.run(COMPOSE_CMD + ["logs"], cwd=root, capture_output=True, text=True)
        _compose(["down"], cwd=root)
        raise RuntimeError(f"Services failed to start:\n{logs.stdout}")
    yield base_url
    compose_logs = subprocess.run(COMPOSE_CMD + ["logs"], cwd=root, capture_output=True, text=True)
    _compose(["down"], cwd=root)
    assert "ERROR" not in compose_logs.stdout


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


def test_gateway_orchestrator_flow(compose_stack):
    base_url = compose_stack
    resp = requests.post(f"{base_url}/orchestrator/start", timeout=5)
    resp.raise_for_status()
    assert isinstance(resp.json().get("pid"), int)

    status = requests.get(f"{base_url}/orchestrator/status", timeout=5).json()
    assert status["running"] is True

    resp = requests.post(
        f"{base_url}/tasks",
        json={"description": "gw", "command": "echo gw"},
        timeout=5,
    )
    resp.raise_for_status()
    task_id = resp.json()["id"]

    root = Path(__file__).resolve().parents[2]
    result = None
    for _ in range(20):
        out = _fetch_result(task_id, root)
        if out and out != "None":
            result = out
            break
        time.sleep(0.5)

    assert result is not None
    stdout, stderr, code = eval(result)
    assert stdout.strip() == "gw"
    assert stderr == ""
    assert code == 0

    stop = requests.post(f"{base_url}/orchestrator/stop", timeout=5)
    assert stop.status_code == 200
    final = requests.get(f"{base_url}/orchestrator/status", timeout=5).json()
    assert final["running"] is False
