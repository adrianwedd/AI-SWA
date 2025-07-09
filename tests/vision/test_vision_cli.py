import os
import subprocess
import sys
from pathlib import Path

import yaml


def _task(id, ubv, tc, rr, size):
    return {
        "id": id,
        "description": "",
        "component": "vision",
        "dependencies": [],
        "priority": 1,
        "status": "pending",
        "user_business_value": ubv,
        "time_criticality": tc,
        "risk_reduction": rr,
        "job_size": size,
    }


def test_vision_cli_ranking(tmp_path):
    tasks = [
        _task(1, 10, 2, 1, 5),  # score 2.6
        _task(2, 5, 1, 1, 2),   # score 3.5
        _task(3, 8, 0, 0, 4),   # score 2.0
    ]
    tasks_file = tmp_path / "tasks.yml"
    tasks_file.write_text(yaml.safe_dump(tasks, sort_keys=False))

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "vision.cli", str(tasks_file)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0
    ordered = yaml.safe_load(result.stdout)
    assert [item["id"] for item in ordered] == [2, 1, 3]


def test_vision_cli_help(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "vision.cli", "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_vision_cli_missing_file(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    result = subprocess.run(
        [sys.executable, "-m", "vision.cli", str(tmp_path / "missing.yml")],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    assert result.returncode != 0
