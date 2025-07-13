"""Optional Rust-backed diff helpers."""

from __future__ import annotations

try:
    from rust_ext import unified_diff  # type: ignore
except Exception:  # pragma: no cover - fallback when extension missing
    import difflib

    def unified_diff(original: str, updated: str, filename: str = "file") -> str:
        """Return unified diff of ``original`` and ``updated``."""
        orig_lines = original.splitlines(keepends=True)
        new_lines = updated.splitlines(keepends=True)
        diff = difflib.unified_diff(
            orig_lines,
            new_lines,
            fromfile=f"{filename}.orig",
            tofile=f"{filename}.new",
        )
        return "".join(diff)

