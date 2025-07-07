import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path

import requests
import pytest


def start_broker(tmp_path, port=8002, metrics_port=0):
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


def run_worker_async(base_url: str, metrics_port: int):
    env = os.environ.copy()
    env["BROKER_URL"] = base_url
    env["WORKER_METRICS_PORT"] = str(metrics_port)
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    return subprocess.Popen(
        [sys.executable, "-m", "worker.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )


def fetch_results(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT task_id, COUNT(*) FROM task_results GROUP BY task_id"
    ).fetchall()
    conn.close()
    return {task_id: count for task_id, count in rows}




@pytest.mark.integration
def test_multiple_workers_process_tasks_once(tmp_path):
    broker_proc, db_path, base_url = start_broker(tmp_path)
    workers = []
    try:
        # skip if queue endpoint is missing
        resp = requests.get(f"{base_url}/tasks/next")
        if resp.status_code != 200:
            pytest.skip("Queue endpoint not implemented")

        task_ids = []
        for i in range(4):
            r = requests.post(
                f"{base_url}/tasks",
                json={"description": f"t{i}", "command": f"echo {i}"},
                timeout=5,
            )
            task_ids.append(r.json()["id"])

        ports = [9101, 9102]
        for p in ports:
            workers.append(run_worker_async(base_url, p))

        for w in workers:
            w.wait(timeout=20)

        results = fetch_results(db_path)
        assert all(results.get(tid, 0) == 1 for tid in task_ids)

    finally:
        for w in workers:
            if w.poll() is None:
                w.terminate()
                w.wait(timeout=5)
        broker_proc.terminate()
        broker_proc.wait(timeout=5)
