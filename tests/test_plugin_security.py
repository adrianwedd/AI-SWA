import os
import json
import base64
import hashlib
import hmac
import zipfile
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


def test_policy_rejects_disallowed_permissions(tmp_path, monkeypatch):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"plugins": {"demo": {"permissions": ["read_files"]}}}))
    monkeypatch.setenv("PLUGIN_POLICY_FILE", str(policy))
    data = {
        "id": "demo",
        "name": "Demo Plugin",
        "version": "0.1",
        "permissions": ["network"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_manifest(manifest_path)


def test_policy_rejects_unknown_plugin(tmp_path, monkeypatch):
    policy = tmp_path / "policy.json"
    policy.write_text(json.dumps({"plugins": {"foo": {"permissions": ["read_files"]}}}))
    monkeypatch.setenv("PLUGIN_POLICY_FILE", str(policy))
    data = {
        "id": "bar",
        "name": "Bar Plugin",
        "version": "0.1",
        "permissions": ["read_files"],
    }
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        load_manifest(manifest_path)


def test_package_example_plugin(tmp_path):
    from scripts.package_plugin import create_plugin_archive

    archive_path = create_plugin_archive(Path("plugins/example_plugin"))
    assert archive_path.exists()
    with zipfile.ZipFile(archive_path) as zf:
        names = zf.namelist()

    assert "manifest.json" in names
    assert "plugin.py" in names
    for name in names:
        assert not name.endswith(".pyc")
        assert "__pycache__" not in name


def test_package_tech_debt_plugin(tmp_path):
    """Tech debt analyzer should package correctly."""
    from scripts.package_plugin import create_plugin_archive

    archive_path = create_plugin_archive(Path("plugins/tech_debt_analyzer"))
    assert archive_path.exists()
    with zipfile.ZipFile(archive_path) as zf:
        names = zf.namelist()

    assert "manifest.json" in names
    assert "plugin.py" in names

