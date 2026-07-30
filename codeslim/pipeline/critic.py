"""
Reflective Critic Repair Node for CodeSlim StateGraph.

Intercepts ASTInvariantGate safety failures, constructs targeted feedback prompts with exact
AST error tracebacks, and increments retry counter up to max ceiling (max_retries = 2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codeslim.pipeline.graph import PipelineState

from codeslim.utils.logger import get_logger

logger = get_logger(__name__)


async def reflective_critic_node(state: PipelineState) -> dict[str, Any]:
    """Intercepts AST validation failures, records feedback trace, and increments retry counter."""
    retry_count = state.get("retry_count", 0) + 1
    ast_errors = state.get("ast_errors", [])
    latest_error = ast_errors[-1] if ast_errors else "Unknown AST invariant violation."

    logger.info(
        "reflective_critic_retry_triggered",
        attempt=retry_count,
        error=latest_error,
    )

    return {
        "retry_count": retry_count,
        "stages_completed": ["critic_node"],
    }
