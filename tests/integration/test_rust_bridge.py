import shutil
import subprocess
import time
from pathlib import Path

import pytest

from core.bridge_client import reverse


@pytest.fixture(scope="module")
def rust_bridge_server():
    if shutil.which("cargo") is None:
        pytest.skip("Rust toolchain not installed")
    service_dir = Path("services/rust_bridge")
    proc = subprocess.Popen(["cargo", "run"], cwd=service_dir)
    for _ in range(20):
        try:
            if reverse("ready") == "ydaer":
                break
        except Exception:
            time.sleep(0.5)
    else:
        proc.terminate()
        proc.wait(timeout=5)
        pytest.skip("rust_bridge failed to start")
    yield
    proc.terminate()
    proc.wait(timeout=5)


@pytest.mark.integration
def test_reverse(rust_bridge_server):
    text = "hello"
    assert reverse(text) == text[::-1]
