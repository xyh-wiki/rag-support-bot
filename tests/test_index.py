"""Tests for the self-refreshing document index."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.index import DocumentIndex


def test_hot_reload_picks_up_new_file(tmp_path):
    (tmp_path / "a.md").write_text("# Billing\n\nRefunds within 14 days.", encoding="utf-8")
    # check_interval=0 + synchronous rebuild → deterministic test
    idx = DocumentIndex(tmp_path, check_interval=0.0, background=False)
    assert not idx.retriever.search("password reset email")

    (tmp_path / "b.md").write_text("# Login\n\nPassword reset emails may land in spam.",
                                   encoding="utf-8")
    hits = idx.retriever.search("password reset email")
    assert hits and hits[0][0].doc_name == "b"


def test_hot_reload_survives_bad_state(tmp_path):
    f = tmp_path / "a.md"
    f.write_text("# Billing\n\nRefunds within 14 days.", encoding="utf-8")
    idx = DocumentIndex(tmp_path, check_interval=0.0, background=False)

    f.unlink()  # docs dir now empty → rebuild fails → old index kept
    assert idx.retriever.search("refunds")
