"""Core package containing orchestrator components."""

try:
    from .io_client import ping as io_ping  # re-export helper
except Exception:  # pragma: no cover - optional grpc dependency
    def io_ping(*_args, **_kwargs) -> str:
        """Fallback when ``grpc`` is unavailable."""
        raise ImportError("grpc is required for io_ping")

from .qa_agent import QAAgent
from .docs_agent import DocsAgent
from .supervisor import Supervisor

__all__ = ["io_ping", "QAAgent", "DocsAgent", "Supervisor"]

