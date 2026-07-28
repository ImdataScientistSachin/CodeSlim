"""
Unit tests for AST Syntax & Signature Preservation Validator.
"""

from codeslim.optimizer.validator import validate_refactored_code


def test_valid_refactored_code():
    original = "def hello():\n    print('hi')\n\ndef world():\n    pass\n"
    optimized = "def hello():\n    print('hi')\n\ndef world():\n    return None\n"
    result = validate_refactored_code(original, optimized)
    assert result.is_valid is True
    assert result.error_message is None
    assert result.missing_signatures == []


def test_syntax_error_in_optimized_code():
    original = "def hello():\n    pass\n"
    optimized = "def hello(\n    pass\n"  # Missing closing parenthesis
    result = validate_refactored_code(original, optimized)
    assert result.is_valid is False
    assert "Syntax error" in result.error_message


def test_missing_function_signature():
    original = "def keep_me():\n    pass\n\ndef remove_me():\n    pass\n"
    optimized = "def keep_me():\n    pass\n"  # remove_me is gone
    result = validate_refactored_code(original, optimized)
    assert result.is_valid is False
    assert "remove_me" in result.missing_signatures


def test_class_signature_preserved():
    original = "class MyClass:\n    pass\n\ndef helper():\n    pass\n"
    optimized = "class MyClass:\n    pass\n\ndef helper():\n    return 1\n"
    result = validate_refactored_code(original, optimized)
    assert result.is_valid is True
