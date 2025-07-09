import yaml
from pathlib import Path
from core.evaluator import Evaluator


def test_critique_scoring(tmp_path):
    log = tmp_path / "c.yml"
    ev = Evaluator(log)
    result = ev.critique({"id": 1, "description": "sample", "status": "done"})
    assert result["score"] == 10
    ev.reflect([{"id": 1, "description": "sample", "status": "done"}])
    data = yaml.safe_load(log.read_text())
    assert "1" in data


