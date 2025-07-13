import argparse
import json
import logging
import subprocess
from pathlib import Path

from core.plugins import load_manifest
from scripts.package_plugin import create_plugin_archive
from services.plugin_marketplace import pipeline
import requests

from core.log_utils import configure_logging


def _request(args: argparse.Namespace, method: str, path: str, **kwargs) -> requests.Response:
    url = f"{args.marketplace_url.rstrip('/')}{path}"
    headers = kwargs.pop("headers", {})
    if args.auth_token:
        headers["Authorization"] = f"Bearer {args.auth_token}"
    elif args.auth_user and args.auth_pass:
        kwargs["auth"] = (args.auth_user, args.auth_pass)
    kwargs["headers"] = headers
    return requests.request(method, url, **kwargs)


def _cmd_validate(args: argparse.Namespace) -> None:
    manifest = load_manifest(Path(args.plugin) / "manifest.json")
    logging.info("Manifest for '%s' version %s is valid", manifest.id, manifest.version)


def _cmd_package(args: argparse.Namespace) -> None:
    # Validate manifest before packaging
    load_manifest(Path(args.plugin) / "manifest.json")
    archive = create_plugin_archive(Path(args.plugin))
    logging.info("Created archive at %s", archive)


def _cmd_sign(args: argparse.Namespace) -> None:
    archive = Path(args.archive)
    sig_path = archive.with_suffix(archive.suffix + ".sig")
    env = {"COSIGN_EXPERIMENTAL": "1"}
    if args.password:
        env["COSIGN_PASSWORD"] = args.password
    cmd = [
        "cosign",
        "sign-blob",
        "--key",
        args.key,
        str(archive),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    sig_path.write_text(result.stdout)
    logging.info("Signature written to %s", sig_path)


def _cmd_upload(args: argparse.Namespace) -> None:
    plugin_dir = Path(args.plugin)
    manifest = load_manifest(plugin_dir / "manifest.json")
    archive = create_plugin_archive(plugin_dir)
    with open(archive, "rb") as fh:
        files = {"file": (archive.name, fh, "application/zip")}
        data = {
            "name": manifest.name,
            "version": manifest.version,
            "dependencies": json.dumps(manifest.dependencies),
        }
        resp = _request(args, "PUT", f"/plugins/{manifest.id}", files=files, data=data)
    if resp.status_code != 200:
        raise SystemExit(f"Error: {resp.status_code} {resp.text}")
    logging.info("Plugin published to marketplace")


def _cmd_update(args: argparse.Namespace) -> None:
    plugin_dir = Path(args.plugin)
    manifest = load_manifest(plugin_dir / "manifest.json")
    archive = create_plugin_archive(plugin_dir)
    with open(archive, "rb") as fh:
        files = {"file": (archive.name, fh, "application/zip")}
        data = {
            "name": manifest.name,
            "version": manifest.version,
            "dependencies": json.dumps(manifest.dependencies),
        }
        resp = _request(args, "PUT", f"/plugins/{manifest.id}", files=files, data=data)
    if resp.status_code != 200:
        raise SystemExit(f"Error: {resp.status_code} {resp.text}")
    logging.info("Plugin updated in marketplace")


def _cmd_remove(args: argparse.Namespace) -> None:
    resp = _request(args, "DELETE", f"/plugins/{args.plugin_id}")
    if resp.status_code != 200:
        raise SystemExit(f"Error: {resp.status_code} {resp.text}")
    logging.info("Plugin removed from marketplace")


def _cmd_review(args: argparse.Namespace) -> None:
    resp = _request(
        args,
        "POST",
        f"/plugins/{args.plugin_id}/reviews",
        json={"rating": args.rating, "review": args.text},
    )
    if resp.status_code != 200:
        raise SystemExit(f"Error: {resp.status_code} {resp.text}")
    logging.info("Review submitted")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plugin management utilities")
    parser.add_argument(
        "--marketplace-url",
        default="http://localhost:8003",
        help="Plugin marketplace base URL",
    )
    parser.add_argument("--auth-token", help="Bearer token for authentication")
    parser.add_argument("--auth-user", help="Basic auth username")
    parser.add_argument("--auth-pass", help="Basic auth password")
    sub = parser.add_subparsers(dest="command", required=True)

    validate_p = sub.add_parser("validate", help="Validate plugin manifest")
    validate_p.add_argument("plugin", help="Path to plugin directory")
    validate_p.set_defaults(func=_cmd_validate)

    package_p = sub.add_parser("package", help="Create plugin archive")
    package_p.add_argument("plugin", help="Path to plugin directory")
    package_p.set_defaults(func=_cmd_package)

    sign_p = sub.add_parser("sign", help="Sign plugin archive with cosign")
    sign_p.add_argument("archive", help="Path to plugin archive")
    sign_p.add_argument("--key", required=True, help="Path to cosign key")
    sign_p.add_argument("--password", help="cosign key password")
    sign_p.set_defaults(func=_cmd_sign)

    upload_p = sub.add_parser("upload", help="Upload plugin to marketplace")
    upload_p.add_argument("plugin", help="Path to plugin directory")
    upload_p.set_defaults(func=_cmd_upload)

    update_p = sub.add_parser("update", help="Update plugin in marketplace")
    update_p.add_argument("plugin", help="Path to plugin directory")
    update_p.set_defaults(func=_cmd_update)

    remove_p = sub.add_parser("remove", help="Remove plugin from marketplace")
    remove_p.add_argument("plugin_id", help="Plugin ID")
    remove_p.set_defaults(func=_cmd_remove)

    review_p = sub.add_parser("review", help="Submit a review for a plugin")
    review_p.add_argument("plugin_id", help="Plugin ID")
    review_p.add_argument("rating", type=int, help="Rating 1-5")
    review_p.add_argument("text", help="Review text")
    review_p.set_defaults(func=_cmd_review)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging()
    args.func(args)


if __name__ == "__main__":
    main()
