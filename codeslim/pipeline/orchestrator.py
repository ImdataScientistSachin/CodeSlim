"""
Pipeline State Machine Orchestrator for CodeSlim.

Routes execution through LangGraph StateGraph engine (`compiled_graph`).
"""

from pathlib import Path
from typing import Any, cast

from codeslim.models.report import CodeSlimReport
from codeslim.pipeline.graph import compiled_graph
from codeslim.pipeline.nodes import report_node
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.pipeline.orchestrator")


class PipelineOrchestrator:
    """State machine pipeline runner for CodeSlim backed by LangGraph StateGraph."""

    def __init__(self, max_token_budget: int = 4096) -> None:
        self.max_token_budget = max_token_budget

    async def run_pipeline(self, file_path: Path, no_llm: bool = False) -> CodeSlimReport:
        """
        Execute full pipeline on target file via LangGraph StateGraph.

        Args:
            file_path: Path to Python source file.
            no_llm: If True, skips LLM invocation node (analysis-only mode).

        Returns:
            CodeSlimReport model containing metrics, bloat map, and diffs.
        """
        log.info("starting_langgraph_pipeline_execution", file=file_path.name, no_llm=no_llm)

        raw_code = file_path.read_text(encoding="utf-8")

        initial_state: dict[str, Any] = {
            "target_path": str(file_path.resolve()),
            "raw_code": raw_code,
            "no_llm": no_llm,
            "retry_count": 0,
            "sensor_results": {},
            "ast_errors": [],
            "stages_completed": [],
            "errors": [],
        }

        final_state = await compiled_graph.ainvoke(cast(Any, initial_state))

        # Assemble CodeSlimReport from final state
        report_state = {
            "file_path": file_path,
            "raw_code": raw_code,
            "file_metrics": final_state.get("file_metrics"),
            "pruned_code": final_state.get("pruned_code", raw_code),
            "bloat_score": final_state.get("bloat_score", 0.0),
            "tokens_saved": final_state.get("tokens_saved", 0),
            "optimized_code": final_state.get("optimized_code"),
            "diff": final_state.get("unified_diff"),
            "errors": final_state.get("errors", []),
            "stages_completed": final_state.get("stages_completed", []),
        }

        res = report_node(report_state)

        log.info(
            "langgraph_pipeline_execution_finished",
            file=file_path.name,
            stages=len(final_state.get("stages_completed", [])),
            errors=len(final_state.get("errors", [])),
        )

        return res["report"]

