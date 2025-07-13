from pathlib import Path
import yaml

from core.researcher import Researcher


def test_search_across_docs_and_tasks(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "intro.md").write_text("vector search introduction")

    tasks_file = tmp_path / "tasks.yml"
    tasks = [
        {"id": 1, "description": "implement vector search", "dependencies": [], "priority": 1, "status": "done"},
    ]
    tasks_file.write_text(yaml.safe_dump(tasks))

    r = Researcher(docs_path=[docs], tasks_files=[tasks_file])
    results = [name for name, _ in r.search("vector search")]
    assert any("intro.md" in n for n in results)
    assert any("tasks.yml:1" in n for n in results)
