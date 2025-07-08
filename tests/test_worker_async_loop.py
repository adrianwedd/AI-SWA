import os
import sys
import time
import subprocess
import sqlite3
from pathlib import Path

import requests
import pytest


def start_broker(tmp_path, port=8003, metrics_port=0):
    env = os.environ.copy()
    env["DB_PATH"] = str(tmp_path / "api.db")
    env["BROKER_METRICS_PORT"] = str(metrics_port)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "broker.main:app",
            "--port",
            str(port),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    base = f"http://localhost:{port}"
    for _ in range(20):
        try:
            requests.get(f"{base}/tasks", timeout=1)
            break
        except requests.RequestException:
            time.sleep(0.2)
    return proc, env["DB_PATH"], base


def run_worker(base_url, concurrency):
    env = os.environ.copy()
    env["BROKER_URL"] = base_url
    env["WORKER_METRICS_PORT"] = "0"
    env["WORKER_CONCURRENCY"] = str(concurrency)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    return subprocess.run(
        [sys.executable, "-m", "worker.main"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def fetch_results(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT task_id, COUNT(*) FROM task_results GROUP BY task_id"
    ).fetchall()
    conn.close()
    return {task_id: count for task_id, count in rows}


@pytest.mark.integration
def test_tasks_run_in_parallel(tmp_path):
    broker_proc, db_path, base_url = start_broker(tmp_path)
    try:
        cmd = "python3 -c 'import time; time.sleep(0.5)'"
        ids = []
        for _ in range(2):
            resp = requests.post(
                f"{base_url}/tasks",
                json={"description": "sleep", "command": cmd},
                timeout=5,
            )
            ids.append(resp.json()["id"])

        start = time.time()
        result = run_worker(base_url, concurrency=2)
        duration = time.time() - start
        assert result.returncode == 0
        assert duration < 2.5
        results = fetch_results(db_path)
        assert all(results.get(tid, 0) == 1 for tid in ids)
    finally:
        broker_proc.terminate()
        broker_proc.wait(timeout=5)

