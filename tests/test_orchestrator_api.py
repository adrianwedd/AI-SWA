import os
import time
from importlib import reload

from fastapi.testclient import TestClient


def setup_module(module):
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_KEY"] = "secret"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    global api
    import services.orchestrator_api as api_mod
    api = reload(api_mod)


def teardown_module(module):
    if api._proc and api._proc.poll() is None:
        api._proc.terminate()
        api._proc.wait(timeout=5)
    os.environ.pop("API_KEY")
    os.environ.pop("API_TOKENS")


def test_start_stop_status():
    client = TestClient(api.app)
    headers = {"X-API-Key": "secret", "Authorization": "Bearer admintoken"}

    # initially not running
    resp = client.get("/status", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["running"] is False

    resp = client.post("/start", headers=headers)
    assert resp.status_code == 200
    pid = resp.json()["pid"]
    assert isinstance(pid, int)

    # give process a moment
    time.sleep(0.2)

    resp = client.get("/status", headers=headers)
    assert resp.json()["running"] is True

    resp = client.post("/stop", headers=headers)
    assert resp.status_code == 200

    resp = client.get("/status", headers=headers)
    assert resp.json()["running"] is False
