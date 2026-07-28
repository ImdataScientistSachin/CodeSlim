"""
Unit tests for Vulture Dead Code Analyzer (DeadCodeAnalyzer).
"""

from pathlib import Path

from codeslim.analyzers.dead_code import DeadCodeAnalyzer


def test_dead_code_analyzer_finds_unused_function(tmp_path: Path) -> None:
    code = """
def used_function():
    return 42

def unused_helper_function():
    return 100

print(used_function())
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = DeadCodeAnalyzer(min_confidence=60)
    res = analyzer.analyze(test_file)

    assert res["dead_code_count"] >= 1
    dead_names = [item.name for item in res["dead_code"]]
    assert "unused_helper_function" in dead_names


def test_dead_code_analyzer_empty_file(tmp_path: Path) -> None:
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("", encoding="utf-8")

    analyzer = DeadCodeAnalyzer()
    res = analyzer.analyze(empty_file)

    assert res["dead_code_count"] == 0
    assert res["dead_code"] == []
