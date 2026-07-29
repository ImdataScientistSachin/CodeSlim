"""Unit tests for C-Native TreeSitterSensor."""

import tree_sitter

from codeslim.analyzers.tree_sitter_sensor import TreeSitterSensor


def test_tree_sitter_version_assertion() -> None:
    """Verify tree-sitter version is >= 0.26.0 using stdlib tuple comparison."""
    version_tuple = tuple(map(int, tree_sitter.__version__.split(".")))
    assert version_tuple >= (0, 26, 0), f"Expected tree-sitter >= 0.26.0, got {tree_sitter.__version__}"


def test_tree_sitter_sensor_extract_skeleton() -> None:
    """Test extracting function skeletons from sample Python code."""
    sensor = TreeSitterSensor()
    code = """def add_numbers(a: int, b: int) -> int:
    result = a + b
    return result

class MathOps:
    def multiply(self, x: float, y: float) -> float:
        val = x * y
        return val
"""
    skeleton = sensor.extract_skeleton(code)
    assert "def add_numbers(a: int, b: int) -> int:" in skeleton
    assert "class MathOps:" in skeleton
    assert "def multiply(self, x: float, y: float) -> float:" in skeleton
    assert "return result" not in skeleton
    assert "val = x * y" not in skeleton


def test_tree_sitter_sensor_empty_code() -> None:
    """Test handling of empty string."""
    sensor = TreeSitterSensor()
    assert sensor.extract_skeleton("") == ""
