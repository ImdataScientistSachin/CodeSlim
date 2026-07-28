"""
Radon Cyclomatic Complexity Analyzer for CodeSlim.

Wraps radon.complexity.cc_visit to extract per-function cyclomatic complexity
scores and aggregates file-level statistics (max, average, count of complex functions).
"""

from pathlib import Path
from typing import Any

from radon.complexity import cc_visit

from codeslim.analyzers.base import BaseAnalyzer
from codeslim.models.metrics import FunctionMetrics
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.analyzers.complexity")


class ComplexityAnalyzer(BaseAnalyzer):
    """Cyclomatic Complexity analyzer using Radon."""

    def name(self) -> str:
        return "complexity_radon"

    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Compute cyclomatic complexity for all functions in a Python file.

        Args:
            file_path: Path to target source file.

        Returns:
            Dict with keys: functions, max_cc, avg_cc, complex_function_count.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        if not file_path.exists():
            log.error("file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Source file not found: {file_path}")

        code = file_path.read_text(encoding="utf-8")
        empty_result = {"functions": [], "max_cc": 0, "avg_cc": 0.0, "complex_function_count": 0}

        if not code.strip():
            log.info("empty_file_skipped", path=str(file_path))
            return empty_result

        try:
            blocks = cc_visit(code)
        except Exception as exc:
            log.warning("radon_parse_failed", path=str(file_path), error=str(exc))
            return empty_result

        function_metrics: list[FunctionMetrics] = []
        for block in blocks:
            if hasattr(block, "complexity"):
                function_metrics.append(
                    FunctionMetrics(
                        name=block.name,
                        line_start=block.lineno,
                        line_end=getattr(block, "endline", None) or block.lineno,
                        cyclomatic_complexity=block.complexity,
                    )
                )

        if not function_metrics:
            return empty_result

        max_cc = max(f.cyclomatic_complexity for f in function_metrics)
        avg_cc = round(sum(f.cyclomatic_complexity for f in function_metrics) / len(function_metrics), 1)
        complex_count = sum(1 for f in function_metrics if f.cyclomatic_complexity > 10)

        log.info(
            "complexity_analysis_complete",
            file=file_path.name,
            total_functions=len(function_metrics),
            max_cc=max_cc,
            avg_cc=avg_cc,
            complex_count=complex_count,
        )

        return {
            "functions": function_metrics,
            "max_cc": max_cc,
            "avg_cc": avg_cc,
            "complex_function_count": complex_count,
        }
