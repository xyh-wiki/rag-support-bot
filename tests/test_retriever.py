"""Offline tests for ingestion + retrieval (no API key needed)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rag.ingest import load_documents
from rag.retriever import Retriever

DOCS = Path(__file__).parent / "kb"  # frozen copy of the sample KB — tests must not depend on the live docs/


def test_ingest_produces_chunks():
    chunks = load_documents(DOCS)
    assert len(chunks) > 10
    assert all(c.text for c in chunks)


def test_refund_question_hits_billing():
    r = Retriever(load_documents(DOCS))
    hits = r.search("how do I get a refund?")
    assert hits, "expected at least one hit"
    top = hits[0][0]
    assert top.doc_name == "billing"
    assert "refund" in top.text.lower()


def test_502_question_hits_troubleshooting():
    r = Retriever(load_documents(DOCS))
    hits = r.search("my site shows 502 bad gateway")
    assert hits[0][0].doc_name == "troubleshooting"


def test_irrelevant_query_returns_few_or_no_hits():
    r = Retriever(load_documents(DOCS))
    hits = r.search("zzzz qqqq xxxx")
    assert hits == []


def test_cjk_tokenizer_bigrams():
    from rag.retriever import _tokenize
    assert "退款" in _tokenize("退款政策")
    assert "policy" in _tokenize("退款 policy")


def test_chinese_docs_retrievable(tmp_path):
    (tmp_path / "faq.md").write_text("# 退款\n\n## 退款政策\n\n14天内全额退款。", encoding="utf-8")
    r = Retriever(load_documents(tmp_path))
    hits = r.search("退款政策是什么")
    assert hits and hits[0][0].doc_name == "faq"


FIXTURES = Path(__file__).parent / "fixtures"


def test_html_ingest_and_search():
    r = Retriever(load_documents(FIXTURES))
    hits = r.search("how to enable SAML single sign-on")
    assert hits[0][0].section == "SSO configuration"


def test_docx_ingest_and_search():
    r = Retriever(load_documents(FIXTURES))
    hits = r.search("uptime SLA service credits")
    assert hits[0][0].section == "Uptime SLA"


def test_pdf_ingest_and_search():
    r = Retriever(load_documents(FIXTURES))
    hits = r.search("how long are backups retained")
    assert hits[0][0].section == "page 1"


def test_xlsx_ingest_and_search():
    r = Retriever(load_documents(FIXTURES))
    hits = r.search("account locked after wrong password")
    assert hits[0][0].section == "Login tests"
    assert "TC-01" in hits[0][0].text
