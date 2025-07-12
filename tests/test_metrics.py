import requests
import pytest
from core.telemetry import setup_telemetry


@pytest.fixture
def start_broker():
    server, _ = setup_telemetry(service_name="broker", metrics_port=0)
    try:
        yield server.server_port
    finally:
        server.shutdown()


@pytest.fixture
def start_worker():
    server, _ = setup_telemetry(service_name="worker", metrics_port=0)
    try:
        yield server.server_port
    finally:
        server.shutdown()


@pytest.fixture
def start_plugin_marketplace():
    server, _ = setup_telemetry(service_name="plugin_marketplace", metrics_port=0)
    try:
        yield server.server_port
    finally:
        server.shutdown()


def test_broker_metrics(start_broker):
    resp = requests.get(f"http://localhost:{start_broker}/metrics")
    assert resp.status_code == 200


def test_worker_metrics(start_worker):
    resp = requests.get(f"http://localhost:{start_worker}/metrics")
    assert resp.status_code == 200


def test_plugin_marketplace_metrics(start_plugin_marketplace):
    resp = requests.get(f"http://localhost:{start_plugin_marketplace}/metrics")
    assert resp.status_code == 200
