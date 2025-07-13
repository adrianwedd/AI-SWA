from __future__ import annotations

import logging
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable, List, Tuple

import yaml

from .memory import Memory

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
    """Provide semantic search over documentation and tasks."""

    def __init__(
        self,
        docs_path: Path | str | Iterable[str | Path] = "research",
        tasks_files: Iterable[str | Path] | None = None,
    ) -> None:
        configure_logging()
        self.logger = logging.getLogger(__name__)
        if isinstance(docs_path, (str, Path)):
            self.docs_paths = [Path(docs_path)]
        else:
            self.docs_paths = [Path(p) for p in docs_path]
        self.tasks_files = [Path(p) for p in (tasks_files or [])]
        self.store = _VectorStore()
        self._index_documents()
        if self.tasks_files:
            self._index_tasks()

    # ------------------------------------------------------------------
    def _index_documents(self) -> None:
        count = 0
        for path in self.docs_paths:
            if not path.exists():
                self.logger.warning("Docs path %s not found", path)
                continue
            for p in path.rglob("*.md"):
                try:
                    text = p.read_text(encoding="utf-8")
                except Exception as exc:  # pragma: no cover - file errors
                    self.logger.warning("Failed to read %s: %s", p, exc)
                    continue
                self.store.add_document(str(p.relative_to(path)), text)
                count += 1
        self.logger.info("Indexed %d documents", count)

    # ------------------------------------------------------------------
    def _index_tasks(self) -> None:
        count = 0
        mem = Memory(Path(".tmp_index.json"))
        for file in self.tasks_files:
            if not file.exists():
                self.logger.warning("Task file %s not found", file)
                continue
            try:
                tasks = mem.load_tasks(str(file))
            except Exception as exc:  # pragma: no cover - file errors
                self.logger.warning("Failed to read %s: %s", file, exc)
                continue
            for t in tasks:
                parts = []
                if t.title:
                    parts.append(t.title)
                parts.append(t.description)
                self.store.add_document(f"{file.name}:{t.id}", " ".join(parts))
                count += 1
        self.logger.info("Indexed %d tasks", count)

    # ------------------------------------------------------------------
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return top matching document names and similarity scores."""
        return self.store.search(query, top_k)
