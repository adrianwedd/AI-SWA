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


def test_patch_scoring(tmp_path):
    log = tmp_path / "c.yml"
    patch_log = tmp_path / "p.yml"
    ev = Evaluator(log, patch_log=patch_log)
    patch = """diff --git a/file.py b/file.py\n+print('debug')\n"""
    result = ev.critique_patch(patch)
    assert result["score"] < 10
    ev.score_patches([patch])
    data = yaml.safe_load(patch_log.read_text())
    assert "1" in data


