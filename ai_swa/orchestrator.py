"""CLI entry point for the AI-SWA orchestrator.

This module exposes the same CLI as :mod:`core.cli`. Available
subcommands include ``start``, ``stop``, ``status`` and ``list``.
"""
from core.cli import build_parser, main as cli_main

__all__ = ["build_parser", "main"]

def main(argv=None):
    """Run the orchestrator CLI."""
    return cli_main(argv)

if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(main())
