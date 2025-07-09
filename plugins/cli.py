import argparse
import subprocess
from pathlib import Path

from core.plugins import load_manifest
from scripts.package_plugin import create_plugin_archive
from services.plugin_marketplace import pipeline
import requests


def _cmd_validate(args: argparse.Namespace) -> None:
    manifest = load_manifest(Path(args.plugin) / "manifest.json")
    print(f"Manifest for '{manifest.id}' version {manifest.version} is valid")


def _cmd_package(args: argparse.Namespace) -> None:
    # Validate manifest before packaging
    load_manifest(Path(args.plugin) / "manifest.json")
    archive = create_plugin_archive(Path(args.plugin))
    print(f"Created archive at {archive}")


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
    print(f"Signature written to {sig_path}")


def _cmd_upload(args: argparse.Namespace) -> None:
    pipeline.certify_and_publish(Path(args.plugin))
    print("Plugin published to marketplace")


def _cmd_review(args: argparse.Namespace) -> None:
    url = f"{args.url.rstrip('/')}/plugins/{args.plugin_id}/reviews"
    resp = requests.post(url, json={"rating": args.rating, "review": args.text})
    if resp.status_code != 200:
        raise SystemExit(f"Error: {resp.status_code} {resp.text}")
    print("Review submitted")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plugin management utilities")
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

    review_p = sub.add_parser("review", help="Submit a review for a plugin")
    review_p.add_argument("plugin_id", help="Plugin ID")
    review_p.add_argument("rating", type=int, help="Rating 1-5")
    review_p.add_argument("text", help="Review text")
    review_p.add_argument("--url", default="http://localhost:8003", help="Marketplace URL")
    review_p.set_defaults(func=_cmd_review)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
