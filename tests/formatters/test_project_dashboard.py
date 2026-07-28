"""
Unit tests for Project Observatory dashboard formatters.
"""


from codeslim.formatters.project_dashboard import (
    render_codebase_fingerprint,
    render_cross_file_intelligence,
    render_file_treemap,
    render_project_header,
    render_project_health,
    render_top_offenders,
)
from codeslim.models.project_report import (
    CodebaseFingerprint,
    PhantomFunction,
    ProjectReport,
)
from codeslim.models.report import CodeSlimReport


def test_project_dashboard_rendering():
    sample_report = ProjectReport(
        project_path="codeslim/",
        total_files=5,
        total_lines=1200,
        overall_bloat_score=45.2,
        overall_grade="B",
        file_reports=[
            CodeSlimReport(file_path="nodes.py", bloat_score=72.0, original_lines=312),
            CodeSlimReport(file_path="client.py", bloat_score=38.0, original_lines=180),
        ],
        phantom_functions=[
            PhantomFunction(function_name="legacy_shim", file_path="utils.py", line_number=45)
        ],
        hallucination_spread={"fake_pkg": ["nodes.py", "client.py"]},
        fingerprint=CodebaseFingerprint(
            clean_lines=900, dead_lines=150, complex_lines=100, duplicate_lines=50, total_lines=1200
        ),
    )

    header = render_project_header(sample_report)
    health = render_project_health(sample_report)
    treemap = render_file_treemap(sample_report)
    offenders = render_top_offenders(sample_report)
    intelligence = render_cross_file_intelligence(sample_report)
    fingerprint = render_codebase_fingerprint(sample_report)

    assert header is not None
    assert health is not None
    assert treemap is not None
    assert offenders is not None
    assert intelligence is not None
    assert fingerprint is not None
