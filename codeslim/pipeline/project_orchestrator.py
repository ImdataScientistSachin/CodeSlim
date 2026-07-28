"""
Project Orchestrator for CodeSlim.

Scans an entire directory of Python files, runs per-file analysis,
executes cross-file static analysis, and builds the final ProjectReport.
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


class ProjectOrchestrator:
    """Orchestrates multi-file directory scanning and codebase-level reporting."""

    def __init__(self) -> None:
        self.cross_file_analyzer = CrossFileAnalyzer()

    def scan_directory(
        self,
        directory_path: str,
        no_llm: bool = True,
        max_files: int = 50,
    ) -> ProjectReport:
        """
        Scan all Python files in target directory.

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
            py_files = sorted([p for p in dir_path.rglob("*.py") if not p.name.startswith(".")])[:max_files]

        log.info("starting_project_scan", directory=directory_path, file_count=len(py_files))

        pipeline = PipelineOrchestrator()
        file_reports: list[CodeSlimReport] = []
        file_metrics_list: list[FileMetrics] = []
        raw_codes: dict[str, str] = {}

        for file_p in py_files:
            try:
                report: CodeSlimReport = asyncio.run(pipeline.run_pipeline(file_p, no_llm=no_llm))
                file_reports.append(report)
                
                # Read raw code for string pattern matching
                code_text = file_p.read_text(encoding="utf-8")
                raw_codes[file_p.name] = code_text

                # Build synthetic FileMetrics from report data
                dup_ratio = report.metrics.duplication_ratio if report.metrics else 0.0
                metrics = FileMetrics(
                    file_path=str(file_p),
                    total_lines=report.original_lines,
                    duplication_ratio=dup_ratio,
                )
                file_metrics_list.append(metrics)
            except Exception as exc:
                log.warning("file_scan_failed", file=str(file_p), error=str(exc))

        # Perform Cross-File Analysis
        phantoms, spread, fingerprint = self.cross_file_analyzer.analyze_cross_file_metrics(
            file_metrics_list, raw_codes
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
            project_path=str(directory_path),
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
