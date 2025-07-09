import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests


def start_broker(tmp_path: Path, port: int, metrics_port: int):
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


def run_autoscaler(base_url: str, metrics_port: int):
    env = os.environ.copy()
    env["BROKER_URL"] = base_url
    env["BROKER_METRICS_PORT"] = str(metrics_port)
    env["AUTOSCALER_LOOPS"] = "5"
    env["AUTOSCALER_INTERVAL"] = "0.5"
    env["WORKER_METRICS_PORT"] = "0"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "worker.autoscaler"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr


def fetch_results(db_path: str) -> int:
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM task_results").fetchone()[0]
    conn.close()
    return count


def queue_length(port: int) -> int:
    resp = requests.get(f"http://localhost:{port}/metrics")
    for line in resp.text.splitlines():
        if line.startswith("broker_queue_length"):
            return int(float(line.split()[-1]))
    return 0


@pytest.mark.integration
def test_autoscaler_processes_queue(tmp_path):
    metrics_port = 9300
    broker_proc, db_path, base = start_broker(tmp_path, port=8010, metrics_port=metrics_port)
    try:
        for _ in range(2):
            requests.post(
                f"{base}/tasks",
                json={"description": "demo", "command": "echo hi"},
                timeout=5,
            )
        assert queue_length(metrics_port) == 2
        run_autoscaler(base, metrics_port)
        assert fetch_results(db_path) == 2
        assert queue_length(metrics_port) == 0
    finally:
        broker_proc.terminate()
        broker_proc.wait(timeout=5)

