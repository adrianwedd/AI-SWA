"""CLI for the Creative Synthesizer."""

import argparse
import logging
from pathlib import Path
from core.creative_synthesizer import CreativeSynthesizer

from core.log_utils import configure_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate prototype modules")
    parser.add_argument("type", help="Template type")
    parser.add_argument("name", help="Module name (without .py)")
    parser.add_argument("--output", default=".", help="Output directory")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    configure_logging()
    synth = CreativeSynthesizer()
    try:
        path = synth.generate(args.name, args.type, directory=args.output)
    except ValueError as exc:
        parser.error(str(exc))
        return 1
    logging.info(str(path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
