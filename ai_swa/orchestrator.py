"""CLI entry point for the AI-SWA orchestrator."""
from core.cli import build_parser, main as cli_main

__all__ = ["build_parser", "main"]

def main(argv=None):
    """Run the orchestrator CLI."""
    return cli_main(argv)

if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(main())
