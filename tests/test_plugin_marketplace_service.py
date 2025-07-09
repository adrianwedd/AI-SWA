import os
import sqlite3
import os
import requests
import pytest
import time
from importlib import reload
from pathlib import Path

import grpc
from fastapi.testclient import TestClient

from core import plugin_marketplace_pb2 as pb2, plugin_marketplace_pb2_grpc as pb2_grpc

from services.plugin_marketplace import graphql as gql


def setup_module(module):
    tmp = Path(module.__file__).parent
    os.environ["PLUGIN_DB"] = str(tmp / "plugins.db")
    os.environ["PLUGIN_DIR"] = str(tmp)
    os.environ["GRPC_PORT"] = "60052"
    os.environ["METRICS_PORT"] = "0"
    from services.plugin_marketplace import service as svc
    module.svc = reload(svc)
    svc.init_db()
    # insert sample plugin
    svc.add_plugin("demo", "Demo", "0.1.0", [], "demo.zip")
    (tmp / "demo.zip").write_bytes(b"demo")


def teardown_module(module):
    if svc._grpc_server:
        module.svc._grpc_server.stop(None)
        time.sleep(0.2)
    if svc._metrics_server:
        svc._metrics_server.shutdown()


def test_rest_list_download():
    client = TestClient(svc.app)
    resp = client.get("/plugins")
    assert resp.status_code == 200
    data = resp.json()
    assert data[0]["id"] == "demo"

    resp = client.get("/plugins/demo/download")
    assert resp.status_code == 200
    assert resp.content == b"demo"


def test_grpc_list_download():
    with TestClient(svc.app):
        channel = grpc.insecure_channel("localhost:60052")
        stub = pb2_grpc.PluginMarketplaceStub(channel)
        for _ in range(10):
            try:
                resp = stub.ListPlugins(pb2.Empty())
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("gRPC server not ready")
        assert resp.plugins[0].id == "demo"
        data = stub.DownloadPlugin(pb2.PluginRequest(id="demo"))
        assert data.data == b"demo"


def test_graphql_queries():
    client = TestClient(gql.app)

    query = """
    { plugins { id name version downloadUrl } }
    """
    resp = client.post("/", json={"query": query})
    assert resp.status_code == 200
    assert resp.json()["data"]["plugins"][0]["id"] == "demo"

    detail_query = """
    query($id: String!) { plugin(id: $id) { id dependencies downloadUrl } }
    """
    resp = client.post("/", json={"query": detail_query, "variables": {"id": "demo"}})
    assert resp.status_code == 200
    data = resp.json()["data"]["plugin"]
    assert data["dependencies"] == []
    assert data["downloadUrl"].endswith("/plugins/demo/download")


def test_metrics_endpoint():
    port = svc._metrics_server.server_port if svc._metrics_server else None
    if not port:
        pytest.skip("metrics not available")
    resp = requests.get(f"http://localhost:{port}/metrics")
    assert resp.status_code == 200
