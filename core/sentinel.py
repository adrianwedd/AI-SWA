import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class EthicalSentinel:
    """Simple policy checker loading blocked actions from a JSON file."""

    policy_path: Path
    blocked_actions: set[str] | None = None

    def load_policies(self) -> None:
        """Load blocked actions from the policy file."""
        if not self.policy_path.exists():
            self.blocked_actions = set()
            return
        with self.policy_path.open() as f:
            data = json.load(f)
        self.blocked_actions = set(data.get("blocked_actions", []))

    def allows(self, action: str) -> bool:
        """Return True if ``action`` is permitted."""
        if self.blocked_actions is None:
            self.load_policies()
        return action not in self.blocked_actions
