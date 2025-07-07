import os
from core.config import load_config


def test_load_node_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("""\nnode:\n  host: testhost\n  port: 1234\n""")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    cfg = load_config()
    assert cfg["node"]["host"] == "testhost"
    assert cfg["node"]["port"] == 1234


def test_node_env_override(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("node:\n  host: filehost\n  port: 1111\n")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    monkeypatch.setenv("NODE_HOST", "envhost")
    monkeypatch.setenv("NODE_PORT", "2222")
    cfg = load_config()
    assert cfg["node"]["host"] == "envhost"
    assert cfg["node"]["port"] == 2222

