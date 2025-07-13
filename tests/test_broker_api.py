import os
from importlib import reload
from pathlib import Path
import shutil
import subprocess
import time
import requests
import pytest

from fastapi.testclient import TestClient

# Set DB_PATH before importing the broker

def setup_module(module):
    os.environ["DB_PATH"] = str(Path(module.__file__).parent / "test.db")
    os.environ["METRICS_PORT"] = "0"
    global broker
    import broker.main as broker_module
    broker = reload(broker_module)


def test_create_and_get_task(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin,workertoken:worker:worker"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    headers = {"Authorization": "Bearer admintoken"}
    resp = client.post("/tasks", json={"description": "demo"}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "demo"
    task_id = data["id"]

    resp = client.get(f"/tasks/{task_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id

    os.environ.pop("API_TOKENS")


def test_create_task_with_metadata(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    headers = {"Authorization": "Bearer admintoken"}
    resp = client.post("/tasks", json={"description": "demo", "metadata": {"foo": "bar"}}, headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["metadata"] == {"foo": "bar"}

    os.environ.pop("API_TOKENS")


def test_api_key(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_KEY"] = "secret"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    headers = {"Authorization": "Bearer admintoken"}

    resp = client.post("/tasks", json={"description": "demo"})
    assert resp.status_code == 401

    resp = client.post(
        "/tasks",
        json={"description": "demo"},
        headers={"X-API-Key": "secret", **headers},
    )
    assert resp.status_code == 200
    os.environ.pop("API_KEY")
    os.environ.pop("API_TOKENS")


def test_invalid_token(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    resp = client.post(
        "/tasks",
        json={"description": "demo"},
        headers={"Authorization": "Bearer bad"},
    )
    assert resp.status_code == 401
    os.environ.pop("API_TOKENS")


def test_missing_token(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    resp = client.post("/tasks", json={"description": "demo"})
    assert resp.status_code == 401
    os.environ.pop("API_TOKENS")


def test_permission_denied(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin,workertoken:worker:worker"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    resp = client.post(
        "/tasks",
        json={"description": "demo"},
        headers={"Authorization": "Bearer workertoken"},
    )
    assert resp.status_code == 403
    os.environ.pop("API_TOKENS")


def test_next_endpoint_returns_single_task(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin,workertoken:worker:worker"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    admin = {"Authorization": "Bearer admintoken"}
    worker = {"Authorization": "Bearer workertoken"}

    resp = client.post("/tasks", json={"description": "demo", "command": "echo hi"}, headers=admin)
    assert resp.status_code == 200

    resp = client.get("/tasks/next", headers=worker)
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "demo"

    # queue should now be empty
    resp = client.get("/tasks/next", headers=worker)
    assert resp.status_code == 200
    assert resp.json() is None

    os.environ.pop("API_TOKENS")


def test_next_requires_auth(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin,workertoken:worker:worker"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    resp = client.get("/tasks/next")
    assert resp.status_code == 401

    resp = client.get("/tasks/next", headers={"Authorization": "Bearer bad"})
    assert resp.status_code == 401

    os.environ.pop("API_TOKENS")


def test_result_requires_auth(tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin,workertoken:worker:worker"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))
    client = TestClient(broker.app)

    headers = {"Authorization": "Bearer admintoken"}
    resp = client.post("/tasks", json={"description": "demo"}, headers=headers)
    assert resp.status_code == 200
    task_id = resp.json()["id"]

    resp = client.post(f"/tasks/{task_id}/result", json={"stdout": "", "stderr": "", "exit_code": 0})
    assert resp.status_code == 401

    resp = client.post(
        f"/tasks/{task_id}/result",
        json={"stdout": "", "stderr": "", "exit_code": 0},
        headers={"Authorization": "Bearer bad"},
    )
    assert resp.status_code == 401

    os.environ.pop("API_TOKENS")


def _docker_ready() -> bool:
    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run([docker, "info"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _docker_ready(), reason="Docker not available")
def test_broker_container(tmp_path):
    root = Path(__file__).resolve().parents[1]
    image = "broker-test"
    subprocess.run([
        "docker",
        "build",
        "-t",
        image,
        "-f",
        str(root / "broker" / "Dockerfile"),
        str(root),
    ], check=True)

    proc = subprocess.Popen(
        [
            "docker",
            "run",
            "--rm",
            "-p",
            "8001:8000",
            "-e",
            f"DB_PATH={tmp_path/'api.db'}",
            "-e",
            "API_TOKENS=admintoken:admin:admin",
            image,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    try:
        for _ in range(20):
            try:
                r = requests.get("http://localhost:8001/tasks", timeout=1)
                if r.status_code == 200:
                    break
            except requests.RequestException:
                time.sleep(0.5)

        resp = requests.post(
            "http://localhost:8001/tasks",
            json={"description": "demo"},
            headers={"Authorization": "Bearer admintoken"},
        )
        assert resp.status_code == 200
        resp = requests.get(
            "http://localhost:8001/tasks",
            headers={"Authorization": "Bearer admintoken"},
        )
        assert any(t["description"] == "demo" for t in resp.json())
    finally:
        proc.terminate()
        proc.wait(timeout=10)
