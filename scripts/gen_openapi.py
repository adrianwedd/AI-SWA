import json
from pathlib import Path

from fastapi import FastAPI

# Import applications
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import broker.main as broker
import services.orchestrator_api as orch


def dump(app: FastAPI, path: Path) -> None:
    path.write_text(json.dumps(app.openapi(), indent=2) + "\n")


def main() -> None:
    out_dir = Path('docs/api')
    out_dir.mkdir(parents=True, exist_ok=True)
    dump(broker.app, out_dir / 'broker.json')
    dump(orch.app, out_dir / 'orchestrator.json')


if __name__ == '__main__':
    main()
