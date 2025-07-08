import json
import logging
from dataclasses import dataclass
from pathlib import Path
from jsonschema import validate

from .log_utils import configure_logging

DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parents[1] / "policies/policy_schema.json"


@dataclass
class EthicalSentinel:
    """Policy enforcement using a JSON policy definition."""

    policy_path: Path
    audit_log: Path | None = None
    policy_schema_path: Path = DEFAULT_SCHEMA_PATH
    blocked_actions: set[str] | None = None
    logger: logging.Logger | None = None

    def __post_init__(self) -> None:
        configure_logging()
        self.logger = logging.getLogger("policy_audit")
        if self.audit_log and not self.logger.handlers:
            handler = logging.FileHandler(self.audit_log)
            handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
            self.logger.addHandler(handler)
        elif not self.logger.handlers:
            self.logger.addHandler(logging.NullHandler())

    def load_policies(self) -> None:
        """Load blocked actions from the policy file."""
        if not self.policy_path.exists():
            self.blocked_actions = set()
            return
        with self.policy_path.open() as f:
            data = json.load(f)
        if self.policy_schema_path.exists():
            with self.policy_schema_path.open() as f:
                schema = json.load(f)
            validate(data, schema)
        self.blocked_actions = set(data.get("blocked_actions", []))

    def allows(self, action: str) -> bool:
        """Return True if ``action`` is permitted."""
        if self.blocked_actions is None:
            self.load_policies()
        allowed = action not in self.blocked_actions
        if not allowed and self.logger:
            self.logger.info("Action '%s' blocked by policy.", action)
        return allowed
