import os
from pathlib import Path
import pytest
from core.tool_runner import ToolRunner


def test_run_allowed_command(tmp_path):
    runner = ToolRunner(tmp_path, allowed_commands=["echo", "touch"])
    result = runner.run("echo hello")
    assert result.stdout.strip() == "hello"


def test_disallow_command(tmp_path):
    runner = ToolRunner(tmp_path, allowed_commands=["echo"])
    with pytest.raises(PermissionError):
        runner.run(["touch", "file.txt"])


def test_prevent_path_escape(tmp_path):
    runner = ToolRunner(tmp_path, allowed_commands=["touch"])
    with pytest.raises(PermissionError):
        runner.run(["touch", "../outside.txt"])
    assert not Path(tmp_path).parent.joinpath("outside.txt").exists()
