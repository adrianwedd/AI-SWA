import argparse
import json
import logging
from pathlib import Path
import zipfile

from core.log_utils import configure_logging


def create_plugin_archive(plugin_dir: Path) -> Path:
    """Create a zip archive of ``plugin_dir`` in ``dist/`` and return the path."""
    plugin_dir = Path(plugin_dir)
    manifest = json.loads((plugin_dir / "manifest.json").read_text())
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    archive_name = f"{manifest['id']}-{manifest['version']}.zip"
    archive_path = dist_dir / archive_name
    with zipfile.ZipFile(archive_path, "w") as zf:
        for file in plugin_dir.rglob("*"):
            if not file.is_file():
                continue
            if "__pycache__" in file.parts or file.suffix == ".pyc":
                continue
            if file.suffix in {".py", ".json"}:
                zf.write(file, file.relative_to(plugin_dir))
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Package a plugin directory")
    parser.add_argument("plugin_dir", help="Path to plugin directory")
    args = parser.parse_args()
    configure_logging()
    path = create_plugin_archive(Path(args.plugin_dir))
    logging.info("Created archive at %s", path)


if __name__ == "__main__":
    main()
