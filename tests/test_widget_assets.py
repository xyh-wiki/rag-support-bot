"""Regression checks for embeddable widget assets."""

from pathlib import Path


ROOT = Path(__file__).parent.parent


def test_widget_uses_external_stylesheet():
    widget = (ROOT / "static" / "widget.js").read_text(encoding="utf-8")

    assert "<style" not in widget
    assert '${apiBase}/static/widget.css' in widget
    assert (ROOT / "static" / "widget.css").is_file()
