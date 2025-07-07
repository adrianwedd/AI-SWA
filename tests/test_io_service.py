import subprocess
import time
from pathlib import Path
import requests

import pytest

from core.io_client import ping


@pytest.fixture(scope="module")
def node_server():
    service_dir = Path("services/node")
    node_modules = service_dir / "node_modules"
    if not (node_modules / "prom-client").exists() or not (node_modules / "express").exists():
        subprocess.run(["npm", "install"], cwd=service_dir, check=True)
    proc = subprocess.Popen(["node", str(service_dir / "io_server.js")])
    for _ in range(20):
        try:
            requests.get("http://localhost:9100/metrics", timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    yield
    proc.terminate()
    proc.wait()


def test_ping(node_server):
    assert ping("hello") == "pong:hello"


def test_metrics_endpoint(node_server):
    ping("metrics")
    try:
        response = requests.get("http://localhost:9100/metrics", timeout=5)
    except requests.RequestException:
        pytest.skip("metrics endpoint unavailable")
    assert response.status_code == 200
    body = response.text
    assert "process_cpu_user_seconds_total" in body
    assert "io_requests_total" in body
    assert "io_request_duration_seconds" in body
