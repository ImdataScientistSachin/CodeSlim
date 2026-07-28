"""
Unit tests for Unified Diff Generator.
"""

from codeslim.optimizer.diff_generator import generate_unified_diff


def test_diff_with_changes():
    original = "def hello():\n    print('hi')\n"
    optimized = "def hello():\n    print('hello world')\n"
    result = generate_unified_diff(original, optimized, file_path="example.py")
    assert isinstance(result, str)
    assert len(result) > 0
    assert "a/example.py" in result
    assert "b/example.py" in result


def test_diff_no_changes():
    code = "def hello():\n    pass\n"
    result = generate_unified_diff(code, code)
    assert result == ""


def test_diff_addition():
    original = "x = 1\n"
    optimized = "x = 1\ny = 2\n"
    result = generate_unified_diff(original, optimized)
    assert "+y = 2" in result
