"""FastAPI app behavior that does not require network access."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import HTTPException
from starlette.requests import Request

import app
from app import _check_chat_origin, _source_only_answer, _stream_delta_content, robots, sitemap
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


def _request(headers: dict[str, str]) -> Request:
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in headers.items()]
    return Request({
        "type": "http",
        "method": "POST",
        "scheme": "https",
        "path": "/api/chat",
        "query_string": b"",
        "headers": raw_headers,
        "client": ("127.0.0.1", 1234),
        "server": ("bot.example.com", 443),
    })


def test_chat_origin_accepts_same_origin(monkeypatch):
    monkeypatch.setattr(app, "PUBLIC_ORIGIN", "https://bot.example.com")
    _check_chat_origin(_request({
        "host": "bot.example.com",
        "origin": "https://bot.example.com",
        "sec-fetch-site": "same-origin",
    }))


def test_chat_origin_rejects_untrusted_website(monkeypatch):
    monkeypatch.setattr(app, "PUBLIC_ORIGIN", "https://bot.example.com")
    try:
        _check_chat_origin(_request({"host": "bot.example.com", "origin": "https://attacker.example"}))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("untrusted origin was accepted")


def test_chat_origin_requires_origin_header(monkeypatch):
    monkeypatch.setattr(app, "PUBLIC_ORIGIN", "https://bot.example.com")
    try:
        _check_chat_origin(_request({"host": "bot.example.com"}))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("missing origin was accepted")


def test_chat_origin_rejects_cross_site_fetch_metadata(monkeypatch):
    monkeypatch.setattr(app, "PUBLIC_ORIGIN", "https://bot.example.com")
    try:
        _check_chat_origin(_request({
            "host": "bot.example.com",
            "origin": "https://bot.example.com",
            "sec-fetch-site": "cross-site",
        }))
    except HTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("cross-site fetch metadata was accepted")


def test_robots_advertises_public_sitemap_and_blocks_api_crawling():
    body = robots().body.decode()

    assert "Disallow: /api/" in body
    assert "Sitemap: https://bot.xyh.wiki/sitemap.xml" in body


def test_sitemap_route_serves_the_static_xml_asset():
    response = sitemap()

    assert response.path.name == "sitemap.xml"
    assert response.media_type == "application/xml"
