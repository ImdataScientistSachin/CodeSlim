"""
Lizard Cognitive Complexity Analyzer for CodeSlim.

Measures per-function cognitive complexity — how difficult code is to
mentally trace — using the Lizard static analysis library.
"""

from pathlib import Path
from typing import Any

import lizard

from codeslim.analyzers.base import BaseAnalyzer
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.analyzers.cognitive")


class CognitiveAnalyzer(BaseAnalyzer):
    """Cognitive Complexity analyzer using Lizard."""

    def name(self) -> str:
        return "cognitive_lizard"

    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze cognitive complexity for all functions in a Python file.

        Args:
            file_path: Path to target source file.

        Returns:
            Dict with keys: max_cognitive, avg_cognitive, high_cognitive_functions, all_functions.

        Raises:
            FileNotFoundError: If target file does not exist.
        """
        if not file_path.exists():
            log.error("file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Source file not found: {file_path}")

        code = file_path.read_text(encoding="utf-8")
        empty_result: dict[str, Any] = {
            "max_cognitive": 0,
            "avg_cognitive": 0.0,
            "high_cognitive_functions": [],
        }

        if not code.strip():
            return empty_result

        try:
            analysis = lizard.analyze_file(str(file_path))
        except Exception as exc:
            log.warning("lizard_analysis_failed", path=str(file_path), error=str(exc))
            return empty_result

        function_list: list[dict[str, Any]] = []
        high_cognitive: list[dict[str, Any]] = []

        for fn in analysis.function_list:
            fn_data = {
                "name": fn.name,
                "long_name": fn.long_name,
                "line_start": fn.start_line,
                "line_end": fn.end_line,
                "cognitive_complexity": fn.cyclomatic_complexity,
                "nloc": fn.nloc,
                "parameter_count": len(fn.full_parameters),
            }
            function_list.append(fn_data)

            if fn.cyclomatic_complexity > 15:
                high_cognitive.append(fn_data)

        if not function_list:
            return empty_result

        max_cog = max(f["cognitive_complexity"] for f in function_list)
        avg_cog = round(sum(f["cognitive_complexity"] for f in function_list) / len(function_list), 1)

        log.info(
            "cognitive_analysis_complete",
            file=file_path.name,
            max_cognitive=max_cog,
            avg_cognitive=avg_cog,
            high_cognitive_count=len(high_cognitive),
        )

        return {
            "max_cognitive": max_cog,
            "avg_cognitive": avg_cog,
            "high_cognitive_functions": high_cognitive,
            "all_functions": function_list,
        }
