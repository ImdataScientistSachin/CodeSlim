"""
Reflective Critic Repair Node for CodeSlim StateGraph.

Intercepts ASTInvariantGate safety failures, constructs targeted 1-shot AST error
injection prompts with exact error tracebacks and concrete repair exemplars, and
increments retry counter up to max ceiling (max_retries = 2).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codeslim.pipeline.graph import PipelineState

from codeslim.utils.logger import get_logger

logger = get_logger(__name__)

AST_1SHOT_REPAIR_EXEMPLAR = """[1-SHOT AST REPAIR EXEMPLAR]
# Example Violation: Accidental decorator loss or signature modification
# INCORRECT (Rejected by AST Gate):
def fetch_user(user_id):
    if not user_id:
        return None
    return db.query(user_id)

# CORRECT (1-Shot Self-Repair — preserves exact signature, decorators, and typing):
@lru_cache(maxsize=256)
async def fetch_user(self, user_id: str, timeout: float = 5.0) -> dict[str, Any] | None:
    if not user_id:
        return None
    return await self.db.query(user_id, timeout=timeout)
"""


def build_ast_repair_prompt(
    ast_errors: list[str],
    failed_code: str | None = None,
    retry_count: int = 1,
) -> str:
    """
    Constructs a 1-shot AST error injection prompt for targeted self-repair.

    Args:
        ast_errors: List of specific AST violation strings from ASTInvariantGate.
        failed_code: Optional candidate code that failed validation.
        retry_count: Current retry counter (1 or 2).

    Returns:
        Formatted 1-shot prompt instructing the LLM on exact AST repair requirements.
    """
    error_bullets = "\n".join(f"  • {err}" for err in ast_errors) if ast_errors else "  • AST interface invariant violation."

    prompt = (
        f"\n\n[CRITICAL AST INVARIANT CORRECTION - ATTEMPT {retry_count}/2]\n"
        f"Your previous refactored code was rejected by the AST Safety Gate due to invariant failures:\n"
        f"{error_bullets}\n\n"
        f"{AST_1SHOT_REPAIR_EXEMPLAR}\n"
        f"[MANDATORY SELF-REPAIR DIRECTIVES]\n"
        f"1. You MUST restore all original public function/class names, parameters, decorators, and async declarations.\n"
        f"2. Only refactor statements INSIDE function bodies to flatten nesting and introduce guard clauses.\n"
        f"3. Do NOT omit any existing methods, classes, or public signatures.\n"
        f"4. Return ONLY valid, executable Python code with no markdown commentary."
    )
    return prompt


async def reflective_critic_node(state: PipelineState) -> dict[str, Any]:
    """
    Intercepts AST validation failures, records feedback trace, and constructs
    1-shot AST error injection feedback for the refactoring self-repair loop.
    """
    retry_count = state.get("retry_count", 0) + 1
    ast_errors = state.get("ast_errors", [])
    failed_code = state.get("optimized_code")

    critic_feedback = build_ast_repair_prompt(
        ast_errors=ast_errors,
        failed_code=failed_code,
        retry_count=retry_count,
    )

    logger.info(
        "reflective_critic_retry_triggered",
        attempt=retry_count,
        errors_count=len(ast_errors),
        latest_error=ast_errors[-1] if ast_errors else "unknown",
    )

    return {
        "retry_count": retry_count,
        "critic_feedback": critic_feedback,
        "stages_completed": ["critic_node"],
    }
