"""
Unit tests for Report Formatters (JSON, Rich, GitHub PR).
"""

from codeslim.formatters.github_pr_formatter import format_github_pr_report
from codeslim.formatters.json_formatter import format_json_report
from codeslim.formatters.rich_formatter import format_rich_report
from codeslim.models.report import BloatMapEntry, CodeSlimReport


def _sample_report() -> CodeSlimReport:
    return CodeSlimReport(
        file_path="sample.py",
        bloat_score=25.0,
        original_lines=50,
        optimized_lines=40,
        bloat_map=[
            BloatMapEntry(
                bloat_type="dead_code",
                severity="medium",
                line_start=10,
                line_end=15,
                explanation="Unused helper function",
                suggestion="Remove function",
            )
        ],
        diff="--- a/sample.py\n+++ b/sample.py\n- unused()\n",
    )


def test_json_formatter():
    report = _sample_report()
    json_output = format_json_report(report)
    assert '"file_path": "sample.py"' in json_output
    assert '"bloat_score": 25.0' in json_output


def test_rich_formatter():
    report = _sample_report()
    rich_output = format_rich_report(report)
    assert "sample.py" in rich_output
    assert "Bloat Score:" in rich_output
    assert "Grade B" in rich_output


def test_github_pr_formatter():
    report = _sample_report()
    md_output = format_github_pr_report(report)
    assert "## 🚀 CodeSlim Analysis Summary" in md_output
    assert "`sample.py`" in md_output
    assert "<details>" in md_output
