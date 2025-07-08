import os
import time
from importlib import reload

from fastapi.testclient import TestClient


def setup_module(module):
    os.environ["METRICS_PORT"] = "0"
    global api
    import services.orchestrator_api as api_mod
    api = reload(api_mod)


def teardown_module(module):
    if api._proc and api._proc.poll() is None:
        api._proc.terminate()
        api._proc.wait(timeout=5)


def test_start_stop_status():
    client = TestClient(api.app)

    # initially not running
    resp = client.get("/status")
    assert resp.status_code == 200
    assert resp.json()["running"] is False

    resp = client.post("/start")
    assert resp.status_code == 200
    pid = resp.json()["pid"]
    assert isinstance(pid, int)

    # give process a moment
    time.sleep(0.2)

    resp = client.get("/status")
    assert resp.json()["running"] is True

    resp = client.post("/stop")
    assert resp.status_code == 200

    resp = client.get("/status")
    assert resp.json()["running"] is False
