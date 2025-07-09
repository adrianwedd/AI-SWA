"""Plugin management utilities with permission validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List

from jsonschema import validate

from .security import validate_plugin_permissions, verify_plugin_signature
from .config import load_config

POLICY_PATH = Path(__file__).resolve().parents[1] / "plugins" / "policy.json"
POLICY_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "plugins" / "policy_schema.json"
try:
    with open(POLICY_SCHEMA_PATH, "r") as f:
        POLICY_SCHEMA = json.load(f)
except FileNotFoundError:
    POLICY_SCHEMA = {"type": "object"}

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "plugins" / "manifest_schema.json"
with open(SCHEMA_PATH, "r") as f:
    MANIFEST_SCHEMA = json.load(f)


@dataclass
class PluginManifest:
    """Metadata describing a plugin."""

    id: str
    name: str
    version: str
    permissions: List[str]
    dependencies: list[str] = field(default_factory=list)
    compatibility: str | None = None
    signature: str | None = None

    def data_for_signature(self) -> dict:
        data = asdict(self)
        data.pop("signature", None)
        return data


def load_policy() -> dict:
    """Load and validate the plugin policy file if present."""
    cfg = load_config()
    path = Path(cfg["security"].get("plugin_policy_file", POLICY_PATH))
    if not path.exists():
        return {}
    with open(path, "r") as f:
        data = json.load(f)
    validate(instance=data, schema=POLICY_SCHEMA)
    return data


def enforce_policy(manifest: PluginManifest) -> None:
    """Ensure ``manifest`` complies with the configured policy."""
    policy = load_policy()
    if not policy:
        return
    plugins = policy.get("plugins", {})
    allowed = plugins.get(manifest.id)
    if not allowed:
        raise ValueError(f"Plugin '{manifest.id}' not permitted by policy")
    allowed_perms = set(allowed.get("permissions", []))
    if not set(manifest.permissions).issubset(allowed_perms):
        raise ValueError(
            f"Plugin '{manifest.id}' requests disallowed permissions"
        )


def load_manifest(path: Path) -> PluginManifest:
    """Load and validate a plugin manifest from ``path``."""
    with open(path, "r") as f:
        data = json.load(f)
    validate(instance=data, schema=MANIFEST_SCHEMA)
    manifest = PluginManifest(**data)
    validate_plugin_permissions(manifest.permissions)
    if manifest.signature:
        verify_plugin_signature(manifest.data_for_signature(), manifest.signature)
    else:
        if load_config()["security"].get("plugin_signing_key"):
            raise ValueError("Signature required")
    enforce_policy(manifest)
    return manifest


def discover_plugins(plugin_dir: Path) -> list[PluginManifest]:
    """Return manifests for all plugins in ``plugin_dir``."""
    manifests: list[PluginManifest] = []
    for manifest_file in plugin_dir.glob("*/manifest.json"):
        manifests.append(load_manifest(manifest_file))
    return manifests
