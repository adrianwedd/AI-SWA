"""Persistent storage utility for tasks and metadata."""

from pathlib import Path
import json
import yaml
from jsonschema import validate
from dataclasses import asdict
from typing import List
from .task import Task


TASK_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["id", "description", "dependencies", "priority", "status"],
        "properties": {
            "id": {"type": "integer"},
            "description": {"type": "string"},
            "component": {"type": "string"},
            "dependencies": {"type": "array", "items": {"type": "integer"}},
            "priority": {"type": "integer", "minimum": 1, "maximum": 5},
            "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "done"],
            },
            "cost": {"type": "integer", "minimum": 1},
            "command": {"type": ["string", "null"]},
            "task_id": {"type": "string"},
            "title": {"type": "string"},
            "area": {"type": "string"},
            "actionable_steps": {"type": "array", "items": {"type": "string"}},
            "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
            "assigned_to": {"type": ["string", "null"]},
            "epic": {"type": "string"},
            "metadata": {"type": "object"},
        },
        "additionalProperties": True,
    },
}


class Memory:
    """Persist simple JSON state to disk."""

    def __init__(self, path: Path):
        """Initialize the memory store.

        Parameters
        ----------
        path:
            File location for the JSON state.
        """
        self.path = Path(path)

    def load(self):
        """Load and return persisted state or an empty dict."""
        if not self.path.exists():
            return {}
        with self.path.open("r") as fh:
            return json.load(fh)

    def save(self, data):
        """Persist ``data`` to disk as JSON."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as fh:
            json.dump(data, fh)

    # New helper methods for YAML task files
    def load_tasks(self, tasks_file: str) -> List[Task]:
        """Return list of :class:`Task` from a YAML file or an empty list."""
        path = Path(tasks_file)
        if not path.exists():
            return []
        with path.open("r") as fh:
            tasks_data = yaml.safe_load(fh) or []
        validate(instance=tasks_data, schema=TASK_SCHEMA)
        fields = set(Task.__dataclass_fields__.keys())
        tasks = []
        for item in tasks_data:
            base = {k: v for k, v in item.items() if k in fields}
            extra = {k: v for k, v in item.items() if k not in fields}
            if extra:
                meta = base.get("metadata", {}) or {}
                meta.update(extra)
                base["metadata"] = meta
            tasks.append(Task(**base))
        return tasks

    def save_tasks(self, tasks: List[Task], tasks_file: str) -> None:
        """Write list of :class:`Task` to ``tasks_file`` in YAML format."""
        fields = set(Task.__dataclass_fields__.keys())
        tasks_data = []
        for t in tasks:
            t_dict = asdict(t)
            data = {k: v for k, v in t_dict.items() if k in fields and k != "metadata" and v is not None}
            if t_dict.get("metadata"):
                data.update(t_dict["metadata"])
            tasks_data.append(data)
        validate(instance=tasks_data, schema=TASK_SCHEMA)
        path = Path(tasks_file)
        with path.open("w") as fh:
            yaml.safe_dump(tasks_data, fh, sort_keys=False)

    def load_critiques(self, file: str) -> dict:
        """Return critique data from YAML or an empty dict."""
        path = Path(file)
        if not path.exists():
            return {}
        with path.open("r") as fh:
            return yaml.safe_load(fh) or {}

    def save_critiques(self, data: dict, file: str) -> None:
        """Write critique data to ``file``."""
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as fh:
            yaml.safe_dump(data, fh, sort_keys=False)

    def reconcile_tasks(
        self,
        existing: List[Task],
        incoming: List[Task],
        critique_map: dict,
    ) -> List[Task]:
        """Merge tasks while removing duplicates.

        Tasks with the same ``id`` or identical ``description`` are considered
        duplicates. If both versions exist, the variant with the higher critique
        score is kept. Missing fields from the lower scored task are merged into
        the retained one.
        """

        def merge(base: Task, other: Task) -> Task:
            base.dependencies = list(set(base.dependencies) | set(other.dependencies))
            base.priority = max(base.priority, other.priority)
            optional = [
                "component",
                "command",
                "task_id",
                "title",
                "area",
                "actionable_steps",
                "acceptance_criteria",
                "assigned_to",
                "epic",
            ]
            for field in optional:
                if getattr(base, field) is None and getattr(other, field) is not None:
                    setattr(base, field, getattr(other, field))
            if other.metadata:
                meta = base.metadata or {}
                meta.update(other.metadata)
                base.metadata = meta
            return base

        selected: dict[str, tuple[Task, int]] = {}
        id_map: dict[int, str] = {}

        def add_task(task: Task, score_key: str) -> None:
            score = critique_map.get(task.id, {}).get(score_key, 0)
            desc_key = task.description.lower()
            # Prefer deduplication by id when available
            if task.id in id_map:
                key = id_map[task.id]
                existing_task, existing_score = selected[key]
                if score >= existing_score:
                    merged = merge(task, existing_task)
                    selected[key] = (merged, score)
                else:
                    merged = merge(existing_task, task)
                    selected[key] = (merged, existing_score)
                if key != desc_key:
                    # update mapping if description changed
                    selected.pop(desc_key, None)
                    id_map[task.id] = key
            elif desc_key in selected:
                existing_task, existing_score = selected[desc_key]
                if score >= existing_score:
                    merged = merge(task, existing_task)
                    selected[desc_key] = (merged, score)
                else:
                    merged = merge(existing_task, task)
                    selected[desc_key] = (merged, existing_score)
                id_map.setdefault(task.id, desc_key)
            else:
                selected[desc_key] = (task, score)
                id_map[task.id] = desc_key

        for task in existing:
            add_task(task, "existing")

        for task in incoming:
            add_task(task, "new")

        return [t for t, _ in selected.values()]
