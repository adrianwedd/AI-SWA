"""CLI for the Creative Synthesizer."""

import argparse
from pathlib import Path
from core.creative_synthesizer import CreativeSynthesizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate prototype modules")
    parser.add_argument("type", help="Template type")
    parser.add_argument("name", help="Module name (without .py)")
    parser.add_argument("--output", default=".", help="Output directory")
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    synth = CreativeSynthesizer()
    try:
        path = synth.generate(args.name, args.type, directory=args.output)
    except ValueError as exc:
        parser.error(str(exc))
        return 1
    print(path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
