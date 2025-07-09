from __future__ import annotations

import shutil
from pathlib import Path

from core.plugins import load_manifest
from scripts.package_plugin import create_plugin_archive

from .service import update_plugin
from . import service


class ScanError(Exception):
    """Raised when a plugin fails security scans."""


def _run_scans(plugin_dir: Path) -> None:
    """Simulate SCA and SAST checks on ``plugin_dir``."""
    # Fail if requirements mention a known vulnerable package
    req = plugin_dir / "requirements.txt"
    if req.exists() and "vulnpkg" in req.read_text():
        raise ScanError("Dependency vulnerabilities detected")

    # Fail if plugin source contains forbidden pattern
    code = (plugin_dir / "plugin.py").read_text()
    if "FAIL_SCAN" in code:
        raise ScanError("Static analysis failure")


def certify_and_publish(plugin_dir: Path) -> None:
    """Run the certification pipeline and publish to the marketplace."""
    manifest = load_manifest(plugin_dir / "manifest.json")
    _run_scans(plugin_dir)
    archive = create_plugin_archive(plugin_dir)
    dest = Path(service.PLUGIN_DIR) / archive.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(archive, dest)
    update_plugin(
        manifest.id,
        manifest.name,
        manifest.version,
        manifest.dependencies,
        dest.name,
    )
