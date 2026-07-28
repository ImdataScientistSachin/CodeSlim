"""
Unit tests for HTML Observatory Exporter module.
"""

from pathlib import Path

from codeslim.formatters.html_exporter import export_html_report, generate_html_observatory_report
from codeslim.models.project_report import ProjectReport
from codeslim.models.report import CodeSlimReport


def _sample_project_report() -> ProjectReport:
    file_rep = CodeSlimReport(
        file_path="sample.py",
        bloat_score=45.0,
        original_lines=100,
    )
    return ProjectReport(
        project_path="./myproject",
        total_files=1,
        total_lines=100,
        overall_bloat_score=45.0,
        overall_grade="C",
        file_reports=[file_rep],
        phantom_functions=[],
        cross_file_clones=[],
        hallucination_spread={},
    )


def test_generate_html_observatory_report():
    project_report = _sample_project_report()
    html_output = generate_html_observatory_report(project_report)

    assert "<!DOCTYPE html>" in html_output
    assert "CODESLIM PROJECT OBSERVATORY" in html_output
    assert "sample.py" in html_output
    assert "C" in html_output


def test_export_html_report(tmp_path: Path):
    project_report = _sample_project_report()
    out_file = tmp_path / "observatory.html"

    result_path = export_html_report(project_report, out_file)

    assert result_path.exists()
    assert "CODESLIM PROJECT OBSERVATORY" in result_path.read_text(encoding="utf-8")
