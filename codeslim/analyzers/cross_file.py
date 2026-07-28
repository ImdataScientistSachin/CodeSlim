"""
Cross-file static analyzer for CodeSlim.

Analyzes cross-module relationships across an entire codebase:
- Phantom functions (functions defined in one file but never imported anywhere)
- Hallucination spread (fake packages imported across multiple files)
- Codebase composition fingerprinting
"""

import re

import structlog

from codeslim.models.metrics import FileMetrics
from codeslim.models.project_report import CodebaseFingerprint, PhantomFunction

log = structlog.get_logger()


class CrossFileAnalyzer:
    """Analyzes dependencies, phantom functions, and import spread across project files."""

    def __init__(self) -> None:
        pass

    def analyze_cross_file_metrics(
        self,
        file_metrics_list: list[FileMetrics],
        raw_codes: dict[str, str],
    ) -> tuple[list[PhantomFunction], dict[str, list[str]], CodebaseFingerprint]:
        """
        Perform cross-file static analysis across all files.

        Returns:
            Tuple of (phantom_functions, hallucination_spread, codebase_fingerprint)
        """
        hallucination_spread: dict[str, list[str]] = {}

        # 1. Collect all hallucinated / third-party dead imports across the codebase
        for metrics in file_metrics_list:
            file_name = metrics.file_path.split("/")[-1].split("\\")[-1]
            for item in metrics.dead_code:
                if item.code_type == "import":
                    if item.name not in hallucination_spread:
                        hallucination_spread[item.name] = []
                    hallucination_spread[item.name].append(file_name)

        # 2. Scan raw code for any string/name usage of function names
        combined_raw_code = "\n".join(raw_codes.values())

        # 3. Detect Phantom Functions
        phantom_functions: list[PhantomFunction] = []
        for metrics in file_metrics_list:
            file_name = metrics.file_path.split("/")[-1].split("\\")[-1]
            for fn in metrics.functions:
                # Skip private dunder or underscore methods
                if fn.name.startswith("_"):
                    continue
                # Skip main entry points
                if fn.name in ("main", "run", "cli", "app"):
                    continue

                # Count occurrences across combined codebase
                pattern = rf"\b{re.escape(fn.name)}\b"
                matches = re.findall(pattern, combined_raw_code)
                
                # If it only appears once (its definition), it's a phantom function!
                if len(matches) <= 1:
                    phantom_functions.append(
                        PhantomFunction(
                            function_name=fn.name,
                            file_path=file_name,
                            line_number=fn.line_start,
                            docstring="",
                        )
                    )

        # 4. Compute Codebase Fingerprint
        total_lines = sum(m.total_lines for m in file_metrics_list)
        dead_lines = sum(len(m.dead_code) for m in file_metrics_list)
        complex_lines = sum(
            sum(fn.line_end - fn.line_start for fn in m.functions if fn.cyclomatic_complexity > 10)
            for m in file_metrics_list
        )
        duplicate_lines = sum(int(m.total_lines * m.duplication_ratio) for m in file_metrics_list)
        hallucinated_lines = sum(
            sum(1 for item in m.dead_code if item.code_type == "import")
            for m in file_metrics_list
        )

        clean_lines = max(0, total_lines - (dead_lines + complex_lines + duplicate_lines))

        fingerprint = CodebaseFingerprint(
            clean_lines=clean_lines,
            dead_lines=dead_lines,
            complex_lines=complex_lines,
            duplicate_lines=duplicate_lines,
            hallucinated_import_lines=hallucinated_lines,
            total_lines=total_lines,
        )

        log.info(
            "cross_file_analysis_complete",
            phantom_count=len(phantom_functions),
            hallucination_spread_count=len(hallucination_spread),
            total_lines=total_lines,
        )

        return phantom_functions, hallucination_spread, fingerprint
