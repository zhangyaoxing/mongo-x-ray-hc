from pathlib import Path

from x_ray_healthcheck.framework import Framework


def _fake_pdf_conversion(html_file, pdf_file):
    assert Path(html_file).is_file()
    Path(pdf_file).write_bytes(b"%PDF-1.7")


def _assert_all_report_formats(output_folder):
    assert (output_folder / "report.md").is_file()
    html_text = (output_folder / "report.html").read_text(encoding="utf-8")
    assert "@page" in html_text
    assert "size: landscape" in html_text or "size:landscape" in html_text
    assert (output_folder / "report.pdf").read_bytes().startswith(b"%PDF")


def test_healthcheck_pdf_format_writes_all_reports(tmp_path, monkeypatch):
    output_folder = tmp_path / "healthcheck"
    output_folder.mkdir()
    monkeypatch.setattr("x_ray.framework.env", "development")
    monkeypatch.setattr("x_ray.framework.html_to_pdf", _fake_pdf_conversion)
    framework = Framework(
        {
            "checksets": {"default": {"items": []}},
            "item_config": {},
            "template": "healthcheck/full.html",
        }
    )

    framework.output_results(output_folder=f"{output_folder}/", fmt="pdf", open_browser=False)

    _assert_all_report_formats(output_folder)
