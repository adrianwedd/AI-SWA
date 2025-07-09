import os
from importlib import reload

from fastapi.testclient import TestClient


def setup_module(module):
    os.environ["DB_PATH"] = str(module.__file__ + ".db")
    os.environ["METRICS_PORT"] = "0"
    global broker
    import broker.main as broker_module
    broker = reload(broker_module)


def test_create_task_publishes(monkeypatch, tmp_path):
    os.environ["DB_PATH"] = str(tmp_path / "api.db")
    os.environ["METRICS_PORT"] = "0"
    os.environ["API_TOKENS"] = "admintoken:admin:admin"
    broker = reload(__import__("broker.main", fromlist=["app", "init_db"]))

    published: list[int] = []

    def fake_publish(tid: int) -> None:
        published.append(tid)

    monkeypatch.setattr(broker, "publish_task", fake_publish)
    client = TestClient(broker.app)

    resp = client.post("/tasks", json={"description": "demo"}, headers={"Authorization": "Bearer admintoken"})
    assert resp.status_code == 200
    task_id = resp.json()["id"]
    assert published == [task_id]
    os.environ.pop("API_TOKENS")
