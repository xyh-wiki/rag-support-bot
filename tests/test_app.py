"""FastAPI app behavior that does not require network access."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent))

from app import _source_only_answer, _stream_delta_content
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


def test_source_only_answer_can_hide_source_metadata():
    chunk = Chunk(doc_name="policy", section="Refunds", text="Refunds are available within 14 days.")

    answer = _source_only_answer([(chunk, 3.25)], show_sources=False)

    assert "Refunds are available" in answer
    assert "policy" not in answer
    assert "相关度" not in answer


def test_stream_delta_content_ignores_usage_chunk_without_delta():
    event = SimpleNamespace(choices=[SimpleNamespace(delta=None)])

    assert _stream_delta_content(event) is None


def test_stream_delta_content_returns_text():
    event = SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="回答"))])

    assert _stream_delta_content(event) == "回答"
