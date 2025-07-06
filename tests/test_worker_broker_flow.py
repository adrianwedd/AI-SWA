import os
import sys
import time
import sqlite3
import subprocess
from pathlib import Path

import requests


def start_broker(tmp_path, port=8001):
    env = os.environ.copy()
    env["DB_PATH"] = str(tmp_path / "api.db")
    env["METRICS_PORT"] = "0"
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
    url = f"http://localhost:{port}/tasks"
    for _ in range(20):
        try:
            requests.get(url, timeout=1)
            break
        except requests.RequestException:
            time.sleep(0.2)
    return proc, env["DB_PATH"], url[:-6]


def run_worker(base_url):
    env = os.environ.copy()
    env["BROKER_URL"] = base_url
    env["METRICS_PORT"] = "0"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "worker.main"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return result


def fetch_result(db_path, task_id):
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT stdout, stderr, exit_code FROM task_results WHERE task_id=?",
        (task_id,),
    ).fetchone()
    conn.close()
    return row


def task_count(db_path):
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    return count


def test_worker_success_result(tmp_path):
    broker_proc, db_path, base_url = start_broker(tmp_path)
    try:
        resp = requests.post(
            f"{base_url}/tasks",
            json={"description": "demo", "command": "echo hi"},
            timeout=5,
        )
        task_id = resp.json()["id"]
        result = run_worker(base_url)
        assert result.returncode == 0
        stdout, stderr, code = fetch_result(db_path, task_id)
        assert stdout.strip() == "hi"
        assert stderr == ""
        assert code == 0
        assert task_count(db_path) == 1
    finally:
        broker_proc.terminate()
        logs, _ = broker_proc.communicate(timeout=5)
    assert f"POST /tasks/{task_id}/result" in logs


def test_worker_failure_result(tmp_path):
    broker_proc, db_path, base_url = start_broker(tmp_path)
    try:
        cmd = "sh -c 'echo fail >&2; exit 1'"
        resp = requests.post(
            f"{base_url}/tasks",
            json={"description": "fail", "command": cmd},
            timeout=5,
        )
        task_id = resp.json()["id"]
        result = run_worker(base_url)
        assert result.returncode == 0
        stdout, stderr, code = fetch_result(db_path, task_id)
        assert code != 0
        assert "fail" in stderr
    finally:
        broker_proc.terminate()
        logs, _ = broker_proc.communicate(timeout=5)
    assert f"POST /tasks/{task_id}/result" in logs
