"""
AST Syntax & Signature Preservation Validator for CodeSlim.

Validates LLM-generated refactored code by checking Python syntax
and verifying that all public function/class signatures are preserved.
"""

import ast
from dataclasses import dataclass, field

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.optimizer.validator")


@dataclass
class SyntaxValidationResult:
    """Result of AST syntax and signature preservation validation."""

    is_valid: bool
    error_message: str | None = None
    missing_signatures: list[str] = field(default_factory=list)


def _extract_top_level_names(code: str) -> set[str]:
    """Extract top-level function and class names from Python source code."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()

    names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


def validate_refactored_code(original_code: str, optimized_code: str) -> SyntaxValidationResult:
    """
    Validate LLM-generated refactored code.

    Performs two checks:
    1. AST syntax validation via ast.parse().
    2. Signature preservation: ensures all top-level functions/classes
       from the original code still exist in the optimized code.

    Args:
        original_code: The original Python source code.
        optimized_code: The LLM-generated refactored code.

    Returns:
        SyntaxValidationResult with is_valid flag, error details, and
        list of any missing top-level signatures.
    """
    # Check 1: AST syntax validation
    try:
        ast.parse(optimized_code)
    except SyntaxError as exc:
        log.warning("syntax_validation_failed", error=str(exc))
        return SyntaxValidationResult(
            is_valid=False,
            error_message=f"Syntax error in optimized code: {exc}",
        )

    # Check 2: Signature preservation
    original_names = _extract_top_level_names(original_code)
    optimized_names = _extract_top_level_names(optimized_code)

    missing = sorted(original_names - optimized_names)

    if missing:
        log.warning("signatures_missing", missing=missing)
        return SyntaxValidationResult(
            is_valid=False,
            error_message=f"Missing top-level signatures: {', '.join(missing)}",
            missing_signatures=missing,
        )

    log.info("validation_passed")
    return SyntaxValidationResult(is_valid=True)
