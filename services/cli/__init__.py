import argparse
import logging
import sys

import requests

from core.log_utils import configure_logging

DEFAULT_URL = "http://localhost:8002"


def _request(args: argparse.Namespace, method: str, path: str):
    url = f"{args.api_url.rstrip('/')}{path}"
    headers = {"X-API-Key": args.api_key}
    if args.token:
        headers["Authorization"] = f"Bearer {args.token}"
    resp = requests.request(method, url, headers=headers)
    if resp.status_code != 200:
        raise SystemExit(f"Error {resp.status_code}: {resp.text}")
    return resp.json()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Control orchestrator via API")
    parser.add_argument("--api-url", default=DEFAULT_URL, help="Orchestrator API base URL")
    parser.add_argument("--api-key", default="secret", help="X-API-Key header")
    parser.add_argument("--token", help="Bearer auth token")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("start", help="Start orchestrator")
    sub.add_parser("stop", help="Stop orchestrator")
    sub.add_parser("status", help="Check orchestrator status")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging()

    if args.command == "start":
        data = _request(args, "POST", "/start")
        logging.info("Orchestrator started with PID %s", data.get("pid"))
        return 0
    if args.command == "stop":
        data = _request(args, "POST", "/stop")
        logging.info("Orchestrator stopped with PID %s", data.get("pid"))
        return 0
    if args.command == "status":
        data = _request(args, "GET", "/status")
        if data.get("running"):
            logging.info("Orchestrator running with PID %s", data.get("pid"))
            return 0
        logging.info("Orchestrator not running")
        return 1
    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
