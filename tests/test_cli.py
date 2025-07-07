import subprocess
import sys
import os
from pathlib import Path


def test_cli_runs(tmp_path):
    cmd = [
        sys.executable,
        "-m",
        "ai_swa.orchestrator",
        "--memory",
        str(tmp_path / "state.json"),
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        cmd,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0
    assert "Orchestrator running" in result.stdout


def test_cli_help(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "ai_swa.orchestrator", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_cli_unwritable_memory(tmp_path):
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_swa.orchestrator",
            "--memory",
            str(memory_dir),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode != 0


def test_cli_start_stop(tmp_path):
    pid_file = tmp_path / "orch.pid"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    start = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_swa.orchestrator",
            "start",
            "--pid-file",
            str(pid_file),
            "--memory",
            str(tmp_path / "state.json"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert start.returncode == 0
    assert pid_file.exists()

    stop = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_swa.orchestrator",
            "stop",
            "--pid-file",
            str(pid_file),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert stop.returncode == 0
    assert not pid_file.exists()


def test_cli_stop_missing_pid(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "ai_swa.orchestrator",
            "stop",
            "--pid-file",
            str(tmp_path / "none.pid"),
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode != 0
