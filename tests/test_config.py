import os
from config import load_config, reload_config


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


def test_sandbox_config_loaded(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("sandbox:\n  root: /tmp/sbox\n  allowed_commands: [touch]\n")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    cfg = load_config()
    assert cfg["sandbox"]["root"] == "/tmp/sbox"
    assert cfg["sandbox"]["allowed_commands"] == ["touch"]


def test_planner_env_override(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    monkeypatch.setenv("PLANNER_BUDGET", "42")
    cfg = load_config()
    assert cfg["planner"]["budget"] == 42


def test_logging_section(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text(
        "logging:\n  config_file: custom.conf\n  level: DEBUG\n  logfile: run.log\n"
    )
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    cfg = load_config()
    assert cfg["logging"]["config_file"] == "custom.conf"
    assert cfg["logging"]["level"] == "DEBUG"
    assert cfg["logging"]["logfile"] == "run.log"


def test_logging_env_override(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    monkeypatch.setenv("LOG_CONFIG", "foo.conf")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("LOG_FILE", "bar.log")
    cfg = load_config()
    assert cfg["logging"]["config_file"] == "foo.conf"
    assert cfg["logging"]["level"] == "WARNING"
    assert cfg["logging"]["logfile"] == "bar.log"


def test_reload_config(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("node:\n  host: first\n")
    monkeypatch.setenv("CONFIG_FILE", str(cfg_file))
    cfg = load_config()
    assert cfg["node"]["host"] == "first"
    cfg_file.write_text("node:\n  host: second\n")
    reloaded = reload_config()
    assert reloaded["node"]["host"] == "second"

