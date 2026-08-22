"""
Project Orchestrator for CodeSlim.

Scans an entire directory of Python files, runs per-file analysis
concurrently via asyncio.gather(), executes cross-file static analysis,
and builds the final ProjectReport.
"""

import asyncio
from pathlib import Path

import structlog

from codeslim.analyzers.cross_file import CrossFileAnalyzer
from codeslim.models.metrics import FileMetrics
from codeslim.models.project_report import ProjectReport
from codeslim.models.report import CodeSlimReport
from codeslim.pipeline.orchestrator import PipelineOrchestrator

log = structlog.get_logger()

# Optimal concurrency: 8 files × 6 threads each = 48 worker threads max.
# Tuned for Windows where thread creation is cheap but excessive concurrency causes scheduler thrash.
_SCAN_CONCURRENCY = 8


class ProjectOrchestrator:

    """Orchestrates multi-file directory scanning and codebase-level reporting."""

    def __init__(self) -> None:
        self.cross_file_analyzer = CrossFileAnalyzer()

    async def _scan_single_file(
        self,
        file_p: Path,
        pipeline: PipelineOrchestrator,
        no_llm: bool,
        semaphore: asyncio.Semaphore,
    ) -> tuple[CodeSlimReport, FileMetrics, str, str] | None:
        """
        Scan a single Python file through the pipeline, gated by a semaphore.

        Args:
            file_p: Path to the target Python file.
            pipeline: Reused PipelineOrchestrator instance.
            no_llm: Skip LLM refactoring if True.
            semaphore: Concurrency limiter to prevent thread saturation.

        Returns:
            Tuple of (CodeSlimReport, FileMetrics, filename, raw_code) or None on error.
        """
        async with semaphore:
            try:
                report: CodeSlimReport = await pipeline.run_pipeline(file_p, no_llm=no_llm)
                code_text = await asyncio.to_thread(file_p.read_text, encoding="utf-8")
                dup_ratio = report.metrics.duplication_ratio if report.metrics else 0.0
                metrics = FileMetrics(
                    file_path=str(file_p),
                    total_lines=report.original_lines,
                    duplication_ratio=dup_ratio,
                )
                return report, metrics, file_p.name, code_text
            except Exception as exc:
                log.warning("file_scan_failed", file=str(file_p), error=str(exc))
                return None

    async def scan_directory_async(
        self,
        directory_path: str,
        no_llm: bool = True,
        max_files: int = 50,
    ) -> ProjectReport:
        """
        Concurrently scan all Python files via asyncio.gather().

        This is the fast async path — all files analyzed in parallel,
        giving near-linear speedup over the old serial for-loop.

        Args:
            directory_path: Directory path to scan.
            no_llm: If True, run static analysis only (faster, $0 cost).
            max_files: Cap on maximum files to scan.

        Returns:
            ProjectReport aggregated object.
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        if dir_path.is_file():
            py_files = [dir_path]
        else:
            py_files = sorted(
                [p for p in dir_path.rglob("*.py") if not p.name.startswith(".")]
            )[:max_files]

        log.info("starting_project_scan_concurrent", directory=directory_path, file_count=len(py_files))

        # Single shared pipeline instance — graph is stateless per invocation
        pipeline = PipelineOrchestrator()

        # Semaphore caps concurrent scans to prevent thread saturation on Windows
        semaphore = asyncio.Semaphore(_SCAN_CONCURRENCY)

        # Fan-out: up to _SCAN_CONCURRENCY files processed concurrently
        tasks = [self._scan_single_file(fp, pipeline, no_llm, semaphore) for fp in py_files]
        results = await asyncio.gather(*tasks)

        file_reports: list[CodeSlimReport] = []
        file_metrics_list: list[FileMetrics] = []
        raw_codes: dict[str, str] = {}

        for result in results:
            if result is not None:
                report, metrics, fname, code_text = result
                file_reports.append(report)
                file_metrics_list.append(metrics)
                raw_codes[fname] = code_text

        # Cross-file analysis remains sequential (requires full corpus)
        phantoms, spread, fingerprint = await asyncio.to_thread(
            self.cross_file_analyzer.analyze_cross_file_metrics,
            file_metrics_list,
            raw_codes,
        )

        total_lines = sum(r.original_lines for r in file_reports)
        avg_score = (
            sum(r.bloat_score * r.original_lines for r in file_reports) / total_lines
            if total_lines > 0
            else 0.0
        )

        grade = (
            "A" if avg_score < 25
            else ("B" if avg_score < 45
            else ("C" if avg_score < 65
            else "F"))
        )

        project_report = ProjectReport(
            project_path=directory_path,
            total_files=len(file_reports),
            total_lines=total_lines,
            overall_bloat_score=round(avg_score, 1),
            overall_grade=grade,
            file_reports=file_reports,
            phantom_functions=phantoms,
            hallucination_spread=spread,
            fingerprint=fingerprint,
        )

        log.info("project_scan_complete", overall_score=avg_score, grade=grade)
        return project_report

    def scan_directory(
        self,
        directory_path: str,
        no_llm: bool = True,
        max_files: int = 50,
    ) -> ProjectReport:
        """
        Synchronous entry point — runs the concurrent async scanner on a new event loop.

        Maintains backward compatibility for CLI and sync test callers.

        Args:
            directory_path: Directory path to scan.
            no_llm: If True, run static analysis only.
            max_files: Cap on maximum files to scan.

        Returns:
            ProjectReport aggregated object.
        """
        return asyncio.run(self.scan_directory_async(directory_path, no_llm=no_llm, max_files=max_files))
