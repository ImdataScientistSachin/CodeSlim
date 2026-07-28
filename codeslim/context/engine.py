"""
Context Minimizer Engine for CodeSlim.

Orchestrates static analysis metrics, LibCST pruning, bloat score calculation,
and token budgeting into an LLM-ready context payload.
"""

from pathlib import Path
from typing import Any

from codeslim.context.prompts import SYSTEM_ANALYSIS_PROMPT, build_user_prompt
from codeslim.context.pruner import prune_source_code
from codeslim.context.tokenizer import count_tokens, enforce_token_budget
from codeslim.models.metrics import FileMetrics, FunctionMetrics
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.context.engine")


def calculate_bloat_score(file_metrics: FileMetrics | dict[str, Any]) -> float:
    """
    Calculate a normalized bloat score (0.0 to 1.0) for a file.
    Aggregates function CC as a scalar max value.

    Formula:
    BloatScore = 0.35 * min(1.0, max_cc / 25) +
                 0.35 * min(1.0, dead_code_count / 10) +
                 0.15 * min(1.0, nesting_depth / 6) +
                 0.15 * min(1.0, duplication_ratio)
    """
    if isinstance(file_metrics, FileMetrics):
        functions: list[FunctionMetrics] = file_metrics.functions
        dead_code_count = len(file_metrics.dead_code)
        nesting_depth = file_metrics.max_nesting_depth
        dup_ratio = getattr(file_metrics, "duplication_ratio", 0.0)
    else:
        functions_raw = file_metrics.get("functions", [])
        functions = [
            f if isinstance(f, FunctionMetrics) else FunctionMetrics(**f)
            for f in functions_raw
            if isinstance(f, (dict, FunctionMetrics))
        ]
        dead_code_count = len(file_metrics.get("dead_code", []))
        nesting_depth = file_metrics.get("max_nesting_depth", 0)
        dup_ratio = file_metrics.get("duplication_ratio", 0.0)

    # Scalar max cyclomatic complexity calculation
    max_cc = max((f.cyclomatic_complexity for f in functions), default=0)

    cc_norm = min(1.0, max_cc / 25.0)
    dead_norm = min(1.0, dead_code_count / 10.0)
    nesting_norm = min(1.0, nesting_depth / 6.0)
    dup_norm = min(1.0, max(0.0, float(dup_ratio)))

    score = (0.35 * cc_norm) + (0.35 * dead_norm) + (0.15 * nesting_norm) + (0.15 * dup_norm)
    return round(min(1.0, max(0.0, score)), 3)


class ContextEngine:
    """Orchestrates code pruning, bloat scoring, and prompt building."""

    def __init__(self, max_token_budget: int = 4096) -> None:
        self.max_token_budget = max_token_budget

    def minimize_context(
        self,
        file_path: Path,
        raw_code: str,
        file_metrics: FileMetrics | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Prune source code, compute bloat score, and assemble LLM payload.

        Args:
            file_path: Path to target file.
            raw_code: Original source code string.
            file_metrics: Metrics collected from Phase 1 analyzers.

        Returns:
            Dict containing pruned_code, bloat_score, system_prompt, user_prompt, tokens_saved.
        """
        original_tokens = count_tokens(raw_code)

        # Extract dead code line numbers if present
        if isinstance(file_metrics, FileMetrics):
            dead_lines = {item.line for item in file_metrics.dead_code}
            max_cc = file_metrics.max_cc
            dead_count = len(file_metrics.dead_code)
        else:
            dead_lines = {item.get("line", 1) for item in file_metrics.get("dead_code", [])}
            fn_list = file_metrics.get("functions", [])
            max_cc = max(
                (
                    f.get("cyclomatic_complexity", 0) if isinstance(f, dict) else f.cyclomatic_complexity
                    for f in fn_list
                ),
                default=0,
            )
            dead_count = len(file_metrics.get("dead_code", []))

        # LibCST pruning
        pruned_code = prune_source_code(raw_code, dead_code_lines=dead_lines, strip_docstrings=True)

        # Enforce token budget
        budgeted_code = enforce_token_budget(pruned_code, max_tokens=self.max_token_budget)

        final_tokens = count_tokens(budgeted_code)
        tokens_saved = max(0, original_tokens - final_tokens)

        # Calculate bloat score
        bloat_score = calculate_bloat_score(file_metrics)

        # Build isolated prompt payload
        user_prompt = build_user_prompt(
            file_name=file_path.name,
            bloat_score=bloat_score,
            max_cc=max_cc,
            dead_code_count=dead_count,
            pruned_code=budgeted_code,
        )

        log.info(
            "context_minimized",
            file=file_path.name,
            original_tokens=original_tokens,
            final_tokens=final_tokens,
            tokens_saved=tokens_saved,
            bloat_score=bloat_score,
        )

        return {
            "pruned_code": budgeted_code,
            "bloat_score": bloat_score,
            "system_prompt": SYSTEM_ANALYSIS_PROMPT,
            "user_prompt": user_prompt,
            "original_tokens": original_tokens,
            "final_tokens": final_tokens,
            "tokens_saved": tokens_saved,
        }
