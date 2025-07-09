from pathlib import Path

from core.researcher import Researcher


def test_search_ranks_relevant_docs(tmp_path: Path) -> None:
    d1 = tmp_path / "doc1.md"
    d2 = tmp_path / "doc2.md"
    d1.write_text("machine learning improves search")
    d2.write_text("orchestrator handles tasks")

    researcher = Researcher(docs_path=tmp_path)
    results = researcher.search("learning search", top_k=1)
    assert results and results[0][0] == "doc1.md"

