from __future__ import annotations

from pathlib import Path

from .fast_diff import unified_diff


def generate_diff(original: str, updated: str, filename: str = "file") -> str:
    """Return a unified diff for the given contents."""
    return unified_diff(original, updated, filename)


def generate_file_diff(path: Path, new_content: str) -> str:
    """Generate a diff between ``path`` on disk and ``new_content``."""
    if path.exists():
        old = path.read_text()
    else:
        old = ""
    return generate_diff(old, new_content, str(path))
