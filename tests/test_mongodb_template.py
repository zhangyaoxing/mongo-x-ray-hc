"""
Copyright (c) 2026 MongoDB Inc.

DISCLAIMER: THESE CODE SAMPLES ARE PROVIDED FOR EDUCATIONAL AND ILLUSTRATIVE PURPOSES ONLY,
TO DEMONSTRATE THE FUNCTIONALITY OF SPECIFIC MONGODB FEATURES.
THEY ARE NOT PRODUCTION-READY AND MAY LACK THE SECURITY HARDENING, ERROR HANDLING, AND TESTING REQUIRED FOR A LIVE ENVIRONMENT.
YOU ARE RESPONSIBLE FOR TESTING, VALIDATING, AND SECURING THIS CODE WITHIN YOUR OWN ENVIRONMENT BEFORE IMPLEMENTATION.
THIS MATERIAL IS PROVIDED "AS IS" WITHOUT WARRANTY OR LIABILITY.
"""

# `mongodb.html` is the optional MongoDB-styled report template (issue #372).
# Its stylesheet is inlined through {{ style }} - the theme plus the shared
# styles, with no remote stylesheet or font - while the charting and syntax
# highlighting libraries keep loading from the same CDNs as `full.html`.
from pathlib import Path

from mongo_x_ray_hc.framework import Framework

TEMPLATE = "healthcheck/mongodb.html"
TEMPLATE_ROOT = Path(__file__).parent.parent / "src" / "mongo_x_ray_hc" / "templates"


def _render_report(output_folder: Path) -> str:
    framework = Framework(
        {
            "checksets": {"default": {"items": []}},
            "item_config": {},
            "template": TEMPLATE,
        }
    )
    framework.output_results(output_folder=f"{output_folder}/", fmt="html", open_browser=False)
    return next(output_folder.rglob("report.html")).read_text(encoding="utf-8")


def test_mongodb_template_inlines_the_theme(tmp_path):
    html = _render_report(tmp_path)

    # Theme and shared styles are inlined; nothing is fetched as a stylesheet.
    assert "--lg-green-base" in html
    assert "--bgColor-muted" in html
    assert '<link rel="stylesheet"' not in html
    # The theme is appended after the shared styles so it wins the cascade.
    assert html.index("--bgColor-muted") < html.index("--lg-green-base")


def test_mongodb_template_renders_the_report_body(tmp_path):
    html = _render_report(tmp_path)

    assert "<title>Healthcheck Report</title>" in html
    assert 'class="mongo-header"' in html
    assert "outline-header" in html
    assert ">MongoDB<" in html
    assert ">x-ray<" in html
    # The content placeholder is filled in by the framework.
    assert "{{ content }}" not in html
    assert "Deployment Health Check" in html


def test_mongodb_template_keeps_the_chart_libraries():
    template = (TEMPLATE_ROOT / "healthcheck" / "mongodb.html").read_text(encoding="utf-8")

    # Charts and syntax highlighting still come from the CDN, as in full.html.
    assert "cdn.jsdelivr.net/npm/chart.js" in template
    assert "chartjs-plugin-datalabels" in template
    assert "highlight.js" in template
    assert "{{ pre_script }}" in template
    assert "{{ script }}" in template


def test_default_template_does_not_pull_the_theme():
    html = _render_report_with_defaults()

    assert "--lg-green-base" not in html


def _render_report_with_defaults() -> str:
    import tempfile

    output_folder = Path(tempfile.mkdtemp())
    framework = Framework({"checksets": {"default": {"items": []}}, "item_config": {}})
    framework.output_results(output_folder=f"{output_folder}/", fmt="html", open_browser=False)
    return next(output_folder.rglob("report.html")).read_text(encoding="utf-8")
