"""
Vulture Dead Code Analyzer for CodeSlim.

Scans Python source files for unused functions, classes, variables,
and imports using the Vulture static analysis library.
"""

from pathlib import Path
from typing import Any

from vulture import Vulture

from codeslim.analyzers.base import BaseAnalyzer
from codeslim.models.metrics import DeadCodeItem
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.analyzers.dead_code")


class DeadCodeAnalyzer(BaseAnalyzer):
    """Dead code detector using Vulture."""

    def __init__(self, min_confidence: int = 60) -> None:
        """
        Args:
            min_confidence: Minimum confidence threshold (0-100) for reporting findings.
        """
        self.min_confidence = min_confidence

    def name(self) -> str:
        return "dead_code_vulture"

    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Scan a file for unused code elements.

        Args:
            file_path: Path to target Python source file.

        Returns:
            Dict with keys: dead_code (list[DeadCodeItem]), dead_code_count (int).

        Raises:
            FileNotFoundError: If target file does not exist.
        """
        if not file_path.exists():
            log.error("file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Source file not found: {file_path}")

        code = file_path.read_text(encoding="utf-8")
        empty_result: dict[str, Any] = {"dead_code": [], "dead_code_count": 0}

        if not code.strip():
            return empty_result

        try:
            v = Vulture(verbose=False)
            v.scan(code, filename=file_path.name)
            unused_items = v.get_unused_code(min_confidence=self.min_confidence)
        except Exception as exc:
            log.warning("vulture_scan_failed", path=str(file_path), error=str(exc))
            return empty_result

        dead_code_list: list[DeadCodeItem] = []
        for item in unused_items:
            dead_code_list.append(
                DeadCodeItem(
                    name=getattr(item, "name", str(item)),
                    line=getattr(item, "first_lineno", 1),
                    code_type=getattr(item, "typ", "unknown"),
                    confidence=getattr(item, "confidence", 100),
                    message=str(item),
                )
            )

        log.info(
            "dead_code_analysis_complete",
            file=file_path.name,
            dead_code_count=len(dead_code_list),
        )

        return {
            "dead_code": dead_code_list,
            "dead_code_count": len(dead_code_list),
        }
