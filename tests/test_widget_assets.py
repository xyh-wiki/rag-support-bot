"""Regression checks for embeddable widget assets."""

from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_widget_uses_external_stylesheet():
    widget = (ROOT / "static" / "widget.js").read_text(encoding="utf-8")

    assert "<style" not in widget
    assert 'const assetVersion = scriptUrl.search' in widget
    assert '${apiBase}/static/widget.css${assetVersion}' in widget
    assert (ROOT / "static" / "widget.css").is_file()


def test_widget_respects_source_visibility_config():
    widget = (ROOT / "static" / "widget.js").read_text(encoding="utf-8")

    assert "showSources = cfg.show_sources !== false" in widget
    assert 'ev === "sources" && showSources' in widget


def test_public_page_has_accurate_indexable_metadata():
    page = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

    assert "RAG Support Bot Demo" in page
    assert '<link rel="canonical" href="https://bot.xyh.wiki/">' in page
    assert "98% match" not in page
    assert "2.4s" not in page
    assert (ROOT / "static" / "sitemap.xml").is_file()
