"""
Unit tests for Lizard Cognitive Complexity Analyzer (CognitiveAnalyzer).
"""

from pathlib import Path

from codeslim.analyzers.cognitive import CognitiveAnalyzer


def test_cognitive_analyzer_basic(tmp_path: Path) -> None:
    code = """
def complex_nested_logic(a, b, c):
    if a > 0:
        for i in range(b):
            if c:
                print(i)
    return True
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = CognitiveAnalyzer()
    res = analyzer.analyze(test_file)

    assert "max_cognitive" in res
    assert "avg_cognitive" in res
    assert len(res["all_functions"]) == 1
    assert res["all_functions"][0]["name"] == "complex_nested_logic"


def test_cognitive_analyzer_empty_file(tmp_path: Path) -> None:
    empty_file = tmp_path / "empty.py"
    empty_file.write_text("", encoding="utf-8")

    analyzer = CognitiveAnalyzer()
    res = analyzer.analyze(empty_file)

    assert res["max_cognitive"] == 0
    assert res["avg_cognitive"] == 0.0
    assert res["high_cognitive_functions"] == []
