from __future__ import annotations

import logging
import math
import re
from collections import Counter
from pathlib import Path
from typing import List, Tuple

from .log_utils import configure_logging


class _VectorStore:
    """In-memory vector store using simple term frequency vectors."""

    def __init__(self) -> None:
        self.docs: List[str] = []
        self.vectors: List[Counter] = []

    def add_document(self, name: str, text: str) -> None:
        tokens = self._tokenize(text)
        self.docs.append(name)
        self.vectors.append(Counter(tokens))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        q_vec = Counter(self._tokenize(query))
        results = []
        for name, vec in zip(self.docs, self.vectors):
            sim = self._cosine_similarity(q_vec, vec)
            results.append((name, sim))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    # ------------------------------------------------------------------
    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    @staticmethod
    def _cosine_similarity(v1: Counter, v2: Counter) -> float:
        if not v1 or not v2:
            return 0.0
        common = set(v1) & set(v2)
        dot = sum(v1[w] * v2[w] for w in common)
        norm1 = math.sqrt(sum(v * v for v in v1.values()))
        norm2 = math.sqrt(sum(v * v for v in v2.values()))
        if not norm1 or not norm2:
            return 0.0
        return dot / (norm1 * norm2)


class Researcher:
    """Provide semantic search over local research documents."""

    def __init__(self, docs_path: Path | str = "research") -> None:
        configure_logging()
        self.logger = logging.getLogger(__name__)
        self.docs_path = Path(docs_path)
        self.store = _VectorStore()
        self._index_documents()

    # ------------------------------------------------------------------
    def _index_documents(self) -> None:
        if not self.docs_path.exists():
            self.logger.warning("Docs path %s not found", self.docs_path)
            return
        for p in self.docs_path.glob("*.md"):
            try:
                text = p.read_text(encoding="utf-8")
            except Exception as exc:  # pragma: no cover - file errors
                self.logger.warning("Failed to read %s: %s", p, exc)
                continue
            self.store.add_document(p.name, text)
        self.logger.info("Indexed %d documents", len(self.store.docs))

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return top matching document names and similarity scores."""
        return self.store.search(query, top_k)
