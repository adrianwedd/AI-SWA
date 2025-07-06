"""Plugin management utilities with permission validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from .security import validate_plugin_permissions, verify_plugin_signature
from .config import load_config


@dataclass
class PluginManifest:
    """Metadata describing a plugin."""

    id: str
    name: str
    version: str
    permissions: List[str]
    signature: str | None = None

    def data_for_signature(self) -> dict:
        data = asdict(self)
        data.pop("signature", None)
        return data


def load_manifest(path: Path) -> PluginManifest:
    """Load and validate a plugin manifest from ``path``."""
    with open(path, "r") as f:
        data = json.load(f)
    manifest = PluginManifest(**data)
    validate_plugin_permissions(manifest.permissions)
    if manifest.signature:
        verify_plugin_signature(manifest.data_for_signature(), manifest.signature)
    else:
        if load_config()["security"].get("plugin_signing_key"):
            raise ValueError("Signature required")
    return manifest


def discover_plugins(plugin_dir: Path) -> list[PluginManifest]:
    """Return manifests for all plugins in ``plugin_dir``."""
    manifests: list[PluginManifest] = []
    for manifest_file in plugin_dir.glob("*/manifest.json"):
        manifests.append(load_manifest(manifest_file))
    return manifests
