from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Task:
    """Simple representation of a unit of work."""

    id: int
    description: str
    dependencies: List[int]
    priority: int
    status: str
    component: Optional[str] = None
    command: Optional[str] = None
    # Optional extended metadata
    task_id: Optional[str] = None
    title: Optional[str] = None
    area: Optional[str] = None
    actionable_steps: Optional[List[str]] = None
    acceptance_criteria: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    epic: Optional[str] = None
