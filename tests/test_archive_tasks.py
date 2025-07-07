import yaml
from pathlib import Path
from scripts.archive_tasks import archive_tasks, load_tasks_with_header


def test_archive_moves_done_tasks(tmp_path):
    tasks_file = tmp_path / "tasks.yml"
    archive_file = tmp_path / "tasks_archive.yml"

    tasks = [
        {"id": 1, "description": "d", "dependencies": [], "priority": 1, "status": "done"},
        {"id": 2, "description": "p", "dependencies": [], "priority": 1, "status": "pending"},
    ]
    header = ["# jsonschema:", "#   {}"]
    tasks_file.write_text("\n".join(header) + "\n" + yaml.safe_dump(tasks, sort_keys=False))

    count = archive_tasks(tasks_file, archive_file)
    assert count == 1

    header_out, remaining = load_tasks_with_header(tasks_file)
    assert header_out == header
    assert remaining == [tasks[1]]

    _, archived = load_tasks_with_header(archive_file)
    assert archived == [tasks[0]]
