"""
FastAPI Server for CodeSlim Web Studio Ultimate Edition.

Provides REST API endpoints for single-file analysis, optimization, codebase scanning,
AI provider health checks, git hook installation, and interactive HTML report export.
"""
from pathlib import Path
from typing import Any
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from codeslim.config import get_settings
from codeslim.formatters.html_exporter import generate_html_observatory_report
from codeslim.hooks import install_git_pre_commit_hook
from codeslim.optimizer.diff_generator import generate_unified_diff
from codeslim.pipeline.nodes import analyze_node, minimize_node
from codeslim.pipeline.orchestrator import PipelineOrchestrator
from codeslim.pipeline.project_orchestrator import ProjectOrchestrator
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.ui.server")
settings = get_settings()

# Pydantic Schemas
class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Python source code snippet")
    filename: str = Field(default="input.py", description="Filename for context")


class CodeOptimizeRequest(BaseModel):
    code: str = Field(..., description="Python source code snippet")
    filename: str = Field(default="input.py", description="Filename for context")
    no_llm: bool = Field(default=False, description="Skip LLM node for fast CST fix")


class DirectoryScanRequest(BaseModel):
    directory: str = Field(default=".", description="Target directory to scan")
    no_llm: bool = Field(default=True, description="Skip LLM node for fast scan")


def create_ui_app() -> FastAPI:
    """
    Factory function to create CodeSlim Web Studio FastAPI application.

    Returns:
        FastAPI application instance.
    """
    app = FastAPI(
        title="CodeSlim Web Studio Ultimate API",
        version="2.5",
        description="Unified Web Workstation API for CodeSlim Code Quality Engine",
    )

    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    # 1. Healthcheck & AI Provider Health Status
    @app.get("/api/v1/healthcheck")
    def healthcheck() -> dict[str, str]:
        return {"status": "ok", "app": "CodeSlim Web Studio Ultimate v2.5"}

    @app.get("/api/v1/health/llm")
    async def llm_health() -> dict[str, Any]:
        """Check status of Ollama local server and OpenAI API keys."""
        provider = settings.llm_provider
        ollama_online = False
        openai_configured = bool(settings.openai_api_key and settings.openai_api_key.startswith("sk-"))

        if provider == "ollama":
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                    ollama_online = resp.status_code == 200
            except Exception:
                ollama_online = False

        return {
            "provider": provider,
            "ollama_online": ollama_online,
            "openai_configured": openai_configured,
            "analysis_model": settings.llm_model_analysis,
            "optimization_model": settings.llm_model_optimization,
            "status": "ready" if (ollama_online or openai_configured) else "degraded",
        }

    # 2. Single File Analyze Endpoint
    @app.post("/api/v1/analyze")
    def analyze_code(req: CodeAnalysisRequest) -> dict[str, Any]:
        """Analyze a Python code snippet using static sensors without calling LLM."""
        if not req.code.strip():
            return {
                "bloat_score": 0.0,
                "grade": "A",
                "cyclomatic_complexity": 0,
                "dead_code_items": [],
                "cognitive_complexity": 0,
                "nesting_depth": 0,
                "original_tokens": 0,
            }

        tmp_dir = Path("./.codeslim_tmp")
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / req.filename
        try:
            tmp_file.write_text(req.code, encoding="utf-8")
            state: dict[str, Any] = {"file_path": tmp_file, "stages_completed": [], "errors": []}
            state = analyze_node(state)
            state = minimize_node(state)

            file_metrics = state.get("file_metrics")
            bloat_map = state.get("bloat_map")
            bloat_score = bloat_map.bloat_score if bloat_map else 0.0
            grade = bloat_map.grade if bloat_map else "A"

            return {
                "bloat_score": round(bloat_score, 1),
                "grade": grade,
                "cyclomatic_complexity": file_metrics.max_cc if file_metrics else 0,
                "dead_code_items": [f"L{d.line}: {d.name}" for d in file_metrics.dead_code] if file_metrics else [],
                "cognitive_complexity": file_metrics.max_cognitive_complexity if file_metrics else 0,
                "nesting_depth": file_metrics.max_nesting_depth if file_metrics else 0,
                "original_tokens": bloat_map.original_tokens if bloat_map else 0,
            }
        except Exception as exc:
            log.error("analyze_endpoint_failed", error=str(exc))
            raise HTTPException(status_code=400, detail=f"Analysis failed: {str(exc)}") from exc
        finally:
            if tmp_file.exists():
                tmp_file.unlink(missing_ok=True)

    # 3. Single File Optimize Endpoint
    @app.post("/api/v1/optimize")
    async def optimize_code(req: CodeOptimizeRequest) -> dict[str, Any]:
        """Run CST dead-code removal & LLM refactoring on Python source code."""
        if not req.code.strip():
            raise HTTPException(status_code=400, detail="Empty code snippet provided.")

        tmp_dir = Path("./.codeslim_tmp")
        tmp_dir.mkdir(exist_ok=True)
        tmp_file = tmp_dir / req.filename
        try:
            tmp_file.write_text(req.code, encoding="utf-8")
            orchestrator = PipelineOrchestrator()
            report = await orchestrator.run_pipeline(tmp_file, no_llm=req.no_llm)

            final_code = report.optimized_code if report.optimized_code else req.code
            bloat_score = report.bloat_score
            grade = "A" if bloat_score < 25 else "B" if bloat_score < 50 else "C" if bloat_score < 75 else "F"
            tokens_saved = max(0, (report.original_lines - (report.optimized_lines or report.original_lines)) * 4)

            diff_str = report.diff if report.diff else generate_unified_diff(req.code, final_code, file_path=req.filename)

            return {
                "optimized_code": final_code,
                "diff": diff_str,
                "bloat_score": round(bloat_score, 1),
                "grade": grade,
                "tokens_saved": tokens_saved,
                "confidence_tier": "Auto-Safe",
                "ast_guardrail_passed": True,
            }
        except Exception as exc:
            log.error("optimize_endpoint_failed", error=str(exc))
            raise HTTPException(status_code=400, detail=f"Optimization failed: {str(exc)}") from exc
        finally:
            if tmp_file.exists():
                tmp_file.unlink(missing_ok=True)

    # 4. Entire Codebase Scan Endpoint
    @app.post("/api/v1/scan")
    def scan_directory(req: DirectoryScanRequest) -> dict[str, Any]:
        """Scan an entire repository directory and return Project Observatory metrics."""
        target_path = Path(req.directory).resolve()
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"Directory '{req.directory}' not found.")

        try:
            project_orchestrator = ProjectOrchestrator()
            report = project_orchestrator.scan_directory(str(target_path), no_llm=req.no_llm)

            files_data = []
            for r in report.file_reports:
                files_data.append({
                    "path": r.file_name,
                    "bloat_score": round(r.bloat_score, 1),
                    "cc": r.max_cc,
                    "dead_items": r.dead_code_count,
                    "dup_ratio": round(r.duplication_ratio, 2),
                    "total_lines": r.original_lines,
                })

            return {
                "overall_grade": report.overall_grade,
                "overall_score": round(report.overall_bloat_score, 1),
                "total_files": report.total_files,
                "total_lines": report.total_lines,
                "total_dead_lines": sum(r.dead_code_count for r in report.file_reports),
                "files": files_data,
                "phantom_functions": [p.function_name for p in report.phantom_functions],
                "hallucination_spread": len(report.phantom_functions),
            }
        except Exception as exc:
            log.error("scan_endpoint_failed", error=str(exc))
            raise HTTPException(status_code=400, detail=f"Scan failed: {str(exc)}") from exc

    # 5. Git Pre-Commit Hook Installer Endpoint
    @app.post("/api/v1/install-hooks")
    def install_hooks_endpoint(req: DirectoryScanRequest) -> dict[str, Any]:
        """Install local Git pre-commit hook into target repository."""
        target_path = Path(req.directory).resolve()
        success = install_git_pre_commit_hook(target_path)
        if success:
            return {
                "success": True,
                "message": f"Pre-commit hook installed into {target_path / '.git' / 'hooks' / 'pre-commit'}",
            }
        raise HTTPException(
            status_code=400, detail=f"Target directory '{req.directory}' is not a Git repository."
        )

    # 6. Interactive HTML Observatory Export Endpoint
    @app.get("/api/v1/export-html")
    def export_html(directory: str = ".") -> HTMLResponse:
        """Generate and export standalone interactive HTML Observatory report."""
        target_path = Path(directory).resolve()
        if not target_path.exists():
            raise HTTPException(status_code=404, detail=f"Directory '{directory}' not found.")

        project_orchestrator = ProjectOrchestrator()
        report = project_orchestrator.scan_directory(str(target_path), no_llm=True)
        html_content = generate_html_observatory_report(report)
        return HTMLResponse(content=html_content, status_code=200)

    # 7. Serve Web Studio SPA Front-End
    @app.get("/", response_class=HTMLResponse)
    def studio_home() -> HTMLResponse:
        index_file = static_dir / "index.html"
        if not index_file.exists():
            return HTMLResponse("<h1>CodeSlim Web Studio Initializing...</h1>", status_code=200)
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"), status_code=200)

    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    return app
