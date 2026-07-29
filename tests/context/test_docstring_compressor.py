"""Unit tests for pure stdlib DocstringCompressor."""

from codeslim.context.docstring_compressor import DocstringCompressor


def test_compress_docstring_basic() -> None:
    """Test compressing a long docstring with filler words."""
    compressor = DocstringCompressor(target_compression=0.3)
    raw_doc = """Calculate total metrics for the dataset.

    This function is used to calculate the sum of all elements in a list.
    Please note that this is very important and should be executed carefully.
    """
    compressed = compressor.compress_docstring(raw_doc)
    assert "Calculate total metrics" in compressed
    assert len(compressed) <= len(raw_doc)


def test_compress_code_docstrings() -> None:
    """Test compressing docstrings inside Python source code."""
    compressor = DocstringCompressor(target_compression=0.3)
    code = '''def process_data(items: list[int]) -> int:
    """Process all items in the given list.

    This function takes a list of integers and computes the total sum.
    Please note that the list should not be empty.
    """
    return sum(items)
'''
    result = compressor.compress_code_docstrings(code)
    assert "def process_data(items: list[int]) -> int:" in result
    assert "return sum(items)" in result
    assert len(result) <= len(code)
