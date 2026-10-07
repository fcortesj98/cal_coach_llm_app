"""Render the model's Markdown answer as safe HTML for the results page."""

from __future__ import annotations

from markdown_it import MarkdownIt

# CommonMark with raw HTML disabled: any HTML the model emits is escaped,
# so it is safe to insert the result into the page with `|safe`.
_md = MarkdownIt("commonmark", {"html": False, "breaks": True})


def to_html(markdown_text: str) -> str:
    return _md.render(markdown_text or "")
