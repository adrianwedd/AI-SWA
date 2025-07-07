import os
import json
import base64
import hashlib
import hmac
import pytest
from pathlib import Path
from jsonschema.exceptions import ValidationError

from core.plugins import load_manifest, PluginManifest


def sign(data: dict, key: str) -> str:
    payload = json.dumps(data, sort_keys=True).encode()
    return base64.b64encode(hmac.new(key.encode(), payload, hashlib.sha256).digest()).decode()


def test_load_valid_manifest(tmp_path):
    key = "secret"
    os.environ["PLUGIN_SIGNING_KEY"] = key
    data = {
        "id": "demo",
        "name": "Demo Plugin",
        "version": "0.1",
        "permissions": ["read_files"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({**data, "signature": sign(data, key)}))
    manifest = load_manifest(manifest_path)
    assert manifest.id == "demo"
    os.environ.pop("PLUGIN_SIGNING_KEY")


def test_reject_invalid_permission(tmp_path):
    data = {
        "id": "demo",
        "name": "Demo Plugin",
        "version": "0.1",
        "permissions": ["dangerous"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_manifest(manifest_path)


def test_reject_invalid_signature(tmp_path):
    key = "secret"
    os.environ["PLUGIN_SIGNING_KEY"] = key
    data = {
        "id": "demo",
        "name": "Demo Plugin",
        "version": "0.1",
        "permissions": ["read_files"],
        "signature": "bad",
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_manifest(manifest_path)
    os.environ.pop("PLUGIN_SIGNING_KEY")


def test_schema_validation_error(tmp_path):
    """Manifest missing required fields should raise ValidationError."""
    data = {"id": "demo"}
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        load_manifest(manifest_path)
