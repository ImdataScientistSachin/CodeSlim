"""
Unit tests for Radon Complexity Analyzer (ComplexityAnalyzer).
"""

from pathlib import Path

import pytest

from codeslim.analyzers.complexity import ComplexityAnalyzer


def test_complexity_analyzer_basic(tmp_path: Path) -> None:
    code = """
def simple_function(a, b):
    return a + b

def complex_function(x):
    if x > 0:
        if x > 10:
            return "high"
        else:
            return "medium"
    return "low"
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    res = analyzer.analyze(test_file)

    assert len(res["functions"]) == 2
    assert res["max_cc"] == 3
    assert res["complex_function_count"] == 0


def test_complexity_analyzer_empty_file(tmp_path: Path) -> None:
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("", encoding="utf-8")

    analyzer = ComplexityAnalyzer()
    res = analyzer.analyze(empty_file)

    assert res["functions"] == []
    assert res["max_cc"] == 0
    assert res["avg_cc"] == 0.0


def test_complexity_analyzer_file_not_found() -> None:
    analyzer = ComplexityAnalyzer()
    with pytest.raises(FileNotFoundError):
        analyzer.analyze(Path("non_existent_file_xyz.py"))
