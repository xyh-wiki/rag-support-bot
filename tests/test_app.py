"""FastAPI app behavior that does not require network access."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import _source_only_answer
from rag.ingest import Chunk


def test_source_only_answer_returns_markdown_sources():
    chunk = Chunk(
        doc_name="policy",
        section="Refunds",
        text="Refund requests are accepted within 14 days after payment.",
    )

    answer = _source_only_answer([(chunk, 3.25)])

    assert "## 1. policy — Refunds" in answer
    assert "Refund requests" in answer
    assert "相关度: 3.25" in answer


def test_source_only_answer_handles_no_hits():
    assert "No matching source excerpts" in _source_only_answer([])
