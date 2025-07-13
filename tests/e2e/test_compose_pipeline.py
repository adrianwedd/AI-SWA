import subprocess
import shutil
import time
from pathlib import Path

import pytest
import requests

COMPOSE_CMD = ["docker", "compose"]


def _compose(args, cwd, **kwargs):
    return subprocess.run(COMPOSE_CMD + args, cwd=cwd, check=True, **kwargs)


def _docker_ready() -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run([docker, "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def compose_stack():
    if not _docker_ready():
        pytest.skip("Docker not available")
    root = Path(__file__).resolve().parents[2]
    _compose(["up", "-d", "--build", "broker", "worker", "orchestrator"], cwd=root)
    base_url = "http://localhost:8000"
    for _ in range(30):
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


def test_compose_pipeline(compose_stack):
    base_url = compose_stack
    resp = requests.post(
        f"{base_url}/tasks",
        json={"description": "demo", "command": "echo pipeline"},
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
    assert stdout.strip() == "pipeline"
    assert stderr == ""
    assert code == 0

    bmetrics = requests.get("http://localhost:9000/metrics", timeout=5)
    wmetrics = requests.get("http://localhost:9001/metrics", timeout=5)
    assert bmetrics.status_code == 200
    assert wmetrics.status_code == 200
    assert "tasks_executed_total" in wmetrics.text
