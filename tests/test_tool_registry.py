import subprocess
import builtins
import pytest

from core.tool_registry import ToolRegistry


def test_subprocess_requires_confirmation(tmp_path):
    reg = ToolRegistry(tmp_path / "reg.json")
    reg.register("echo")
    reg.hook_subprocess()
    with pytest.raises(PermissionError):
        subprocess.run(["echo", "hi"], capture_output=True, text=True)
    reg.confirm("echo")
    result = subprocess.run(["echo", "hi"], capture_output=True, text=True)
    reg.unhook_subprocess()
    assert result.stdout.strip() == "hi"


def test_filesystem_hook(tmp_path):
    reg = ToolRegistry(tmp_path / "reg.json")
    reg.register("open")
    reg.hook_filesystem()
    with pytest.raises(PermissionError):
        with builtins.open(tmp_path / "f.txt", "w") as f:
            f.write("bad")
    reg.unhook_filesystem()
    reg.confirm("open")
    reg.hook_filesystem()
    with builtins.open(tmp_path / "f.txt", "w") as f:
        f.write("ok")
    reg.unhook_filesystem()
    assert (tmp_path / "f.txt").read_text() == "ok"
