"""Generate small prototype modules from templates."""

from __future__ import annotations

from pathlib import Path
from typing import Dict


class CreativeSynthesizer:
    """Create simple code modules from built-in templates."""

    DEFAULT_TEMPLATES: Dict[str, str] = {
        "module": "\n".join([
            '"""New module."""',
            "",
            "def main() -> None:",
            "    pass",
            "",
            "if __name__ == '__main__':", 
            "    main()",
        ]),
        "cli": "\n".join([
            '"""Command line interface."""',
            "import argparse",
            "",
            "def build_parser() -> argparse.ArgumentParser:",
            "    parser = argparse.ArgumentParser()",
            "    return parser",
            "",
            "def main(argv=None) -> int:",
            "    parser = build_parser()",
            "    parser.parse_args(argv)",
            "    return 0",
            "",
            "if __name__ == '__main__':", 
            "    raise SystemExit(main())",
        ]),
    }

    def __init__(self, templates: Dict[str, str] | None = None) -> None:
        self.templates = {**self.DEFAULT_TEMPLATES, **(templates or {})}

    # ------------------------------------------------------------------
    def available_types(self) -> list[str]:
        """Return list of template names."""
        return sorted(self.templates)

    # ------------------------------------------------------------------
    def generate(self, name: str, module_type: str = "module", directory: str | Path = ".") -> Path:
        """Create a new file ``name`` with the given template."""
        if module_type not in self.templates:
            raise ValueError(f"Unknown template: {module_type}")
        target_dir = Path(directory)
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{name}.py"
        path.write_text(self.templates[module_type])
        return path

