"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

# The report body is markdown that is converted with python-markdown's table
# extension (see BaseFramework.output_results). That extension keeps any line
# that follows a table row inside the table, so a section heading written right
# after an item whose markdown ends with its last row used to be swallowed as
# one more table row - "2.5 Review Shard Key Information" disappeared into the
# server parameters table of "2.4".
import io
import re

import markdown

from mongo_x_ray.table_width_extension import TableWidthExtension
from mongo_x_ray_hc.framework import Framework

# The extensions the HTML report is rendered with.
REPORT_EXTENSIONS = [TableWidthExtension(), "fenced_code", "toc", "md_in_html"]

# A check item body that ends right after its last table row, without a blank
# line - the shape that triggered the bug.
TABLE_WITHOUT_TRAILING_BLANK_LINE = "| Host | Set |\n|---|---|\n| `host1` | `rs0` |"


class _StubItem:
    """Minimal check item whose markdown ends with a table row."""

    def __init__(self, name: str):
        self.name = name
        self.description = f"{name} description."
        self.test_result: dict = {"items": []}

    @property
    def test_result_markdown(self) -> str:
        return TABLE_WITHOUT_TRAILING_BLANK_LINE

    @property
    def review_result_markdown(self) -> str:
        return TABLE_WITHOUT_TRAILING_BLANK_LINE


def _render(items: list) -> str:
    framework = Framework({"checksets": {"default": {"items": []}}, "item_config": {}})
    framework._items = items
    output = io.StringIO()
    framework._render_markdown(output)
    return output.getvalue()


def _default_items() -> list:
    # The order of the default checkset, so the shard key item is "2.5".
    return [
        _StubItem("Build Information"),
        _StubItem("Cluster Information"),
        _StubItem("Server Status Information"),
        _StubItem("Server Parameters"),
        _StubItem("Shard Key Information"),
    ]


def test_every_heading_is_preceded_by_a_blank_line():
    markdown_text = _render(_default_items())
    lines = markdown_text.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("### "):
            assert index > 0, f"{line!r} is the first line"
            assert lines[index - 1].strip() == "", f"missing blank line before {line!r}"
    # The item headings must exist at all: without the blank line the heading is
    # appended to the last table row instead of starting a line of its own.
    for title in ("1.5 Shard Key Information", "2.5 Review Shard Key Information"):
        assert f"\n\n### {title}\n" in markdown_text, f"{title!r} does not start a line"


def test_heading_after_a_table_is_rendered_as_a_heading():
    html = markdown.markdown(_render(_default_items()), extensions=REPORT_EXTENSIONS)
    for level, titles in (
        ("h2", ("1 Review Test Results", "2 Review Raw Results")),
        ("h3", ("1.5 Shard Key Information", "2.5 Review Shard Key Information")),
    ):
        for title in titles:
            assert re.search(rf"<{level}[^>]*>{re.escape(title)}</{level}>", html), (
                f"{title!r} was not rendered as a heading"
            )
            assert f"{title}</td>" not in html, f"{title!r} was swallowed by the previous table"
