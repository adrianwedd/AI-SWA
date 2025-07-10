from __future__ import annotations

"""Generate code patches using a fine-tuned LLM."""

from dataclasses import dataclass
from typing import List, Optional

from core.code_llm import CodeLLM


@dataclass
class ActionGenerator:
    """Wrapper around :class:`CodeLLM` for patch generation."""

    model_path: str = "distilgpt2"
    llm: Optional[CodeLLM] = None

    def __post_init__(self) -> None:
        if self.llm is None:
            self.llm = CodeLLM(model_name=self.model_path)

    def propose(self, context: str, max_tokens: int = 64, num_actions: int = 1) -> List[str]:
        """Return ``num_actions`` proposed code patches for ``context``."""
        if not self.llm:
            return []
        return self.llm.generate_actions(
            context, max_tokens=max_tokens, num_return_sequences=num_actions
        )

