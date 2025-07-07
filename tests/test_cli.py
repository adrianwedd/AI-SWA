import os
import subprocess
import sys
from pathlib import Path


def _run(cmd, tmp_path, env):
    return subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_cli_help(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = _run([sys.executable, "-m", "ai_swa.orchestrator", "--help"], tmp_path, env)
    assert result.returncode == 0
    out = result.stdout.lower()
    assert "start" in out and "stop" in out and "status" in out


def test_cli_start_status_stop(tmp_path):
    pid_file = tmp_path / "orch.pid"
    config = tmp_path / "config.yaml"
    config.write_text("test: true")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])

    start = _run([
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "--config",
        str(config),
        "start",
        "--pid-file",
        str(pid_file),
    ], tmp_path, env)
    assert start.returncode == 0
    assert pid_file.exists()

    status = _run([
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "status",
        "--pid-file",
        str(pid_file),
    ], tmp_path, env)
    assert status.returncode == 0
    assert "running" in status.stdout.lower()

    stop = _run([
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "stop",
        "--pid-file",
        str(pid_file),
    ], tmp_path, env)
    assert stop.returncode == 0
    assert not pid_file.exists()

    status2 = _run([
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "status",
        "--pid-file",
        str(pid_file),
    ], tmp_path, env)
    assert status2.returncode != 0


def test_cli_start_missing_config(tmp_path):
    pid_file = tmp_path / "orch.pid"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = _run([
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "start",
        "--pid-file",
        str(pid_file),
        "--config",
        str(tmp_path / "missing.yaml"),
    ], tmp_path, env)
    assert result.returncode != 0
