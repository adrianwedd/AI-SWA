import os
import subprocess
import sys
from pathlib import Path
from importlib import reload

import requests
from fastapi.testclient import TestClient


def _run(cmd, tmp_path, env):
    return subprocess.run(cmd, cwd=tmp_path, capture_output=True, text=True, env=env, check=False)


def setup_module(module):
    os.environ["METRICS_PORT"] = "0"
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""
    os.environ["OTEL_SDK_DISABLED"] = "true"
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


def test_cli_start_status_stop(tmp_path, monkeypatch):
    client = TestClient(api.app)

    def fake_request(method, url, headers=None, **kwargs):
        path = url.replace("http://localhost:8002", "")
        resp = client.request(method, path, headers=headers, **kwargs)
        class R:
            def __init__(self, resp):
                self.status_code = resp.status_code
                self.text = resp.text
                self._resp = resp
            def json(self):
                return self._resp.json()
        return R(resp)

    monkeypatch.setattr(requests, "request", fake_request)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    status = _run([sys.executable, "-m", "services.cli", "status"], tmp_path, env)
    assert status.returncode != 0

    start = _run([sys.executable, "-m", "services.cli", "start"], tmp_path, env)
    assert start.returncode == 0

    stat2 = _run([sys.executable, "-m", "services.cli", "status"], tmp_path, env)
    assert stat2.returncode == 0

    stop = _run([sys.executable, "-m", "services.cli", "stop"], tmp_path, env)
    assert stop.returncode == 0
    final = _run([sys.executable, "-m", "services.cli", "status"], tmp_path, env)
    assert final.returncode != 0
