from __future__ import annotations

"""Utilities for generating code actions via a fine-tuned LLM."""

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class CodeLLM:
    """Wrapper around a text-generation pipeline for code actions."""

    model_name: str = "distilgpt2"
    pipeline: Optional[Any] = None

    def __post_init__(self) -> None:
        if self.pipeline is None:
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                pipeline as hf_pipeline,
            )

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.pipeline = hf_pipeline(
                "text-generation", model=model, tokenizer=tokenizer
            )

    def generate_actions(
        self, prompt: str, max_tokens: int = 64, num_return_sequences: int = 1
    ) -> List[str]:
        """Return a list of generated code actions."""
        if self.pipeline is None:
            return []
        outputs = self.pipeline(
            prompt, max_new_tokens=max_tokens, num_return_sequences=num_return_sequences
        )
        return [o.get("generated_text", "") for o in outputs]
