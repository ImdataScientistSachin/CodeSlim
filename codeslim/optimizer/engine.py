"""
Optimizer Engine Orchestrator for CodeSlim.

Chains validation, confidence classification, and diff generation
into a single post-LLM optimization pipeline.
"""

from typing import Any

from codeslim.llm.models import LLMRefactorResponse
from codeslim.optimizer.confidence import classify_refactoring_actions
from codeslim.optimizer.diff_generator import generate_unified_diff
from codeslim.optimizer.validator import validate_refactored_code
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.optimizer.engine")


class OptimizerEngine:
    """Post-LLM optimization pipeline orchestrator."""

    def optimize(
        self, original_code: str, llm_response: LLMRefactorResponse, file_path: str = "source.py"
    ) -> dict[str, Any]:
        """
        Run the full post-LLM optimization pipeline.

        Pipeline steps:
        1. Validate refactored code (AST syntax + signature preservation).
        2. If valid: classify actions into 3 confidence tiers.
        3. Generate unified diff between original and optimized code.
        4. Package result dictionary.

        If validation fails, falls back to original code with error details.

        Args:
            original_code: The original Python source code.
            llm_response: Structured LLM refactoring response.
            file_path: File path label for diff headers.

        Returns:
            Dictionary with optimized_code, diff, confidence_tiers,
            validation_passed flag, and error details.
        """
        optimized_code = llm_response.optimized_code

        # Step 1: Validate
        validation = validate_refactored_code(original_code, optimized_code)

        if not validation.is_valid:
            log.warning(
                "optimization_rejected",
                reason=validation.error_message,
                missing=validation.missing_signatures,
            )
            return {
                "validation_passed": False,
                "error_message": validation.error_message,
                "missing_signatures": validation.missing_signatures,
                "optimized_code": original_code,
                "diff": "",
                "confidence_tiers": classify_refactoring_actions([]).model_dump(),
            }

        # Step 2: Classify actions
        tiers = classify_refactoring_actions(llm_response.actions)

        # Step 3: Generate diff
        diff = generate_unified_diff(original_code, optimized_code, file_path=file_path)

        # Step 4: Package result
        log.info("optimization_complete", file=file_path, confidence_score=llm_response.confidence_score)

        return {
            "validation_passed": True,
            "error_message": None,
            "missing_signatures": [],
            "optimized_code": optimized_code,
            "diff": diff,
            "confidence_tiers": tiers.model_dump(),
            "confidence_score": llm_response.confidence_score,
        }
