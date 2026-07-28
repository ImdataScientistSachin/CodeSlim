"""
Unified Diff Generator for CodeSlim.

Produces human-readable unified diff output between original
and optimized source code.
"""

import difflib

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.optimizer.diff_generator")


def generate_unified_diff(
    original_code: str,
    optimized_code: str,
    file_path: str = "source.py",
) -> str:
    """
    Generate a unified diff string between original and optimized code.

    Materializes unified diff output as a string via "".join(diff).

    Args:
        original_code: The original Python source code.
        optimized_code: The LLM-generated refactored code.
        file_path: File path label for diff headers.

    Returns:
        Unified diff string. Empty string if no changes detected.
    """
    original_lines = original_code.splitlines(keepends=True)
    optimized_lines = optimized_code.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        optimized_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm="",
    )

    result = "".join(diff)

    if result:
        log.info("diff_generated", file=file_path, diff_length=len(result))
    else:
        log.info("no_changes_detected", file=file_path)

    return result
