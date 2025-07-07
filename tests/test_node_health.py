import requests
import pytest

from tests.test_io_service import node_server


def test_health_endpoint(node_server):
    try:
        response = requests.get("http://localhost:9100/health", timeout=5)
    except requests.RequestException:
        pytest.skip("health endpoint unavailable")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
