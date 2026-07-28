"""
Code Duplication Analyzer for CodeSlim.

Detects repeated line sequences using n-gram hashing and computes
a duplication ratio representing what fraction of code is duplicated.
"""

from collections import Counter
from pathlib import Path
from typing import Any

from codeslim.analyzers.base import BaseAnalyzer
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.analyzers.duplication")


class DuplicationAnalyzer(BaseAnalyzer):
    """Line-level duplication detector using n-gram hashing."""

    def __init__(self, min_block_lines: int = 3) -> None:
        """
        Args:
            min_block_lines: Minimum consecutive identical lines to consider duplicated.
        """
        self.min_block_lines = min_block_lines

    def name(self) -> str:
        return "duplication_ngram"

    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Compute line-level duplication metrics for a Python file.

        Args:
            file_path: Path to target source file.

        Returns:
            Dict with keys: duplication_ratio, duplicate_line_count, total_non_empty_lines.

        Raises:
            FileNotFoundError: If target file does not exist.
        """
        if not file_path.exists():
            log.error("file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Source file not found: {file_path}")

        code = file_path.read_text(encoding="utf-8")

        # Normalize: strip whitespace, exclude blank lines and comments
        lines = [line.strip() for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]

        if len(lines) < self.min_block_lines * 2:
            return {
                "duplication_ratio": 0.0,
                "duplicate_line_count": 0,
                "total_non_empty_lines": len(lines),
            }

        # Build n-grams and count occurrences
        ngrams: list[tuple[str, ...]] = []
        for i in range(len(lines) - self.min_block_lines + 1):
            ngrams.append(tuple(lines[i : i + self.min_block_lines]))

        ngram_counts = Counter(ngrams)

        # Mark line indices that belong to any repeated block
        duplicated_indices: set[int] = set()
        for i, ngram in enumerate(ngrams):
            if ngram_counts[ngram] > 1:
                for offset in range(self.min_block_lines):
                    duplicated_indices.add(i + offset)

        duplicate_count = len(duplicated_indices)
        ratio = round(duplicate_count / len(lines), 3) if lines else 0.0

        log.info(
            "duplication_analysis_complete",
            file=file_path.name,
            duplication_ratio=ratio,
            duplicate_lines=duplicate_count,
            total_lines=len(lines),
        )

        return {
            "duplication_ratio": ratio,
            "duplicate_line_count": duplicate_count,
            "total_non_empty_lines": len(lines),
        }
