"""
Pipeline State Machine Orchestrator for CodeSlim.

Routes execution through nodes sequentially:
Analyze -> Minimize -> Deterministic Fix -> LLM Refactor -> Guardrails -> Report Assembly.
"""

from pathlib import Path
from typing import Any

from codeslim.models.report import CodeSlimReport
from codeslim.pipeline.nodes import (
    analyze_node,
    deterministic_fix_node,
    guardrail_node,
    llm_refactor_node,
    minimize_node,
    report_node,
)
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.pipeline.orchestrator")


class PipelineOrchestrator:
    """State machine pipeline runner for CodeSlim."""

    def __init__(self, max_token_budget: int = 4096) -> None:
        self.max_token_budget = max_token_budget

    async def run_pipeline(self, file_path: Path, no_llm: bool = False) -> CodeSlimReport:
        """
        Execute full pipeline on target file.

        Args:
            file_path: Path to Python source file.
            no_llm: If True, skips LLM invocation node (analysis-only mode).

        Returns:
            CodeSlimReport model containing metrics, bloat map, and diffs.
        """
        log.info("starting_pipeline_execution", file=file_path.name, no_llm=no_llm)

        state: dict[str, Any] = {
            "file_path": file_path,
            "max_token_budget": self.max_token_budget,
            "no_llm": no_llm,
            "errors": [],
            "stages_completed": [],
        }

        # Step 1: Analyze
        state = analyze_node(state)

        # Step 2: Minimize
        state = minimize_node(state)

        # Step 2.5: Deterministic LibCST Fixes (auto-remove dead imports/variables)
        state = deterministic_fix_node(state)

        # Step 3: LLM Refactor
        state = await llm_refactor_node(state)

        # Step 4: Guardrails & Diff
        state = guardrail_node(state)

        # Step 5: Report Assembly
        state = report_node(state)

        log.info(
            "pipeline_execution_finished",
            file=file_path.name,
            stages=len(state["stages_completed"]),
            errors=len(state["errors"]),
        )

        return state["report"]
