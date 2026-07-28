"""
Unit tests for CrossFileAnalyzer.
"""

from codeslim.analyzers.cross_file import CrossFileAnalyzer
from codeslim.models.metrics import DeadCodeItem, FileMetrics, FunctionMetrics


def test_cross_file_analyzer_phantom_function():
    analyzer = CrossFileAnalyzer()

    metrics1 = FileMetrics(
        file_path="file1.py",
        total_lines=50,
        functions=[
            FunctionMetrics(name="unused_helper", line_start=10, line_end=20, cyclomatic_complexity=2),
            FunctionMetrics(name="used_helper", line_start=25, line_end=35, cyclomatic_complexity=2),
        ],
    )
    metrics2 = FileMetrics(
        file_path="file2.py",
        total_lines=40,
        functions=[
            FunctionMetrics(name="main", line_start=1, line_end=15, cyclomatic_complexity=1),
        ],
    )

    raw_codes = {
        "file1.py": "def unused_helper(): pass\ndef used_helper(): pass",
        "file2.py": "from file1 import used_helper\ndef main(): used_helper()",
    }

    phantoms, hallucination_spread, fingerprint = analyzer.analyze_cross_file_metrics(
        [metrics1, metrics2], raw_codes
    )

    phantom_names = [p.function_name for p in phantoms]
    assert "unused_helper" in phantom_names
    assert "used_helper" not in phantom_names
    assert fingerprint.total_lines == 90


def test_cross_file_hallucination_spread():
    analyzer = CrossFileAnalyzer()

    metrics1 = FileMetrics(
        file_path="a.py",
        total_lines=20,
        dead_code=[DeadCodeItem(name="fake_pkg", line=1, code_type="import", confidence=100)],
    )
    metrics2 = FileMetrics(
        file_path="b.py",
        total_lines=30,
        dead_code=[DeadCodeItem(name="fake_pkg", line=2, code_type="import", confidence=100)],
    )

    raw_codes = {"a.py": "import fake_pkg", "b.py": "import fake_pkg"}

    phantoms, spread, fingerprint = analyzer.analyze_cross_file_metrics([metrics1, metrics2], raw_codes)

    assert "fake_pkg" in spread
    assert set(spread["fake_pkg"]) == {"a.py", "b.py"}
