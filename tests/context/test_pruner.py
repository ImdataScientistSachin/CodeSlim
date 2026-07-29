"""
Unit tests for LibCST Code Pruner.
"""

from codeslim.context.pruner import prune_source_code, remove_dead_functions


def test_prune_docstrings():
    source = '''
"""Module docstring to be removed."""

def add(a: int, b: int) -> int:
    """Function docstring to be removed."""
    return a + b
'''
    pruned = prune_source_code(source, strip_docstrings=True)
    assert '"""Module docstring' not in pruned
    assert '"""Function docstring' not in pruned
    assert "return a + b" in pruned


def test_prune_docstring_empty_body_inserts_pass():
    source = '''
def empty_func():
    """Only docstring in function body."""
'''
    pruned = prune_source_code(source, strip_docstrings=True)
    assert "def empty_func():" in pruned
    assert "pass" in pruned


def test_prune_dead_code_lines():
    source = """line1 = 10
unused_var = 20
line3 = 30"""
    # Suppose Vulture flagged line 2 as unused
    pruned = prune_source_code(source, dead_code_lines={2}, strip_docstrings=False)
    assert "line1 = 10" in pruned
    assert "unused_var = 20" not in pruned
    assert "line3 = 30" in pruned


def test_prune_syntax_error_returns_raw():
    source = "def broken_syntax(:"
    pruned = prune_source_code(source)
    assert pruned == source


def test_remove_dead_functions():
    source = """def used_fn():
    return 42

def legacy_dead_shim():
    print("dead")
    return None
"""
    cleaned = remove_dead_functions(source, {"legacy_dead_shim"})
    assert "used_fn" in cleaned
    assert "legacy_dead_shim" not in cleaned

