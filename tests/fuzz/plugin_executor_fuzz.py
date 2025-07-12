import sys
import shutil
from pathlib import Path

import afl

from plugins.executor import run_plugin


def fuzz_one(data: bytes) -> None:
    tmp = Path("/tmp/afl_plugin")
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    (tmp / "plugin.py").write_text("print('ok')")
    try:
        (tmp / "manifest.json").write_bytes(data)
        run_plugin(tmp)
    except Exception:
        pass


def main() -> None:
    afl.init()
    while afl.loop():
        data = sys.stdin.buffer.read()
        if not data:
            break
        fuzz_one(data)


if __name__ == "__main__":
    main()
