"""
Unit tests for Code Duplication Analyzer (DuplicationAnalyzer).
"""

from pathlib import Path

from codeslim.analyzers.duplication import DuplicationAnalyzer


def test_duplication_analyzer_detects_repeated_blocks(tmp_path: Path) -> None:
    code = """
def process_a():
    x = 10
    y = 20
    z = x + y
    return z

def process_b():
    x = 10
    y = 20
    z = x + y
    return z
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = DuplicationAnalyzer(min_block_lines=3)
    res = analyzer.analyze(test_file)

    assert res["duplication_ratio"] > 0.0
    assert res["duplicate_line_count"] >= 3


def test_duplication_analyzer_clean_code(tmp_path: Path) -> None:
    code = """
def func_one():
    return 1

def func_two():
    return 2
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = DuplicationAnalyzer(min_block_lines=3)
    res = analyzer.analyze(test_file)

    assert res["duplication_ratio"] == 0.0
    assert res["duplicate_line_count"] == 0
