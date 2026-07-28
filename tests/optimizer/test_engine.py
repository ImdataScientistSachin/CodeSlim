"""
Unit tests for Optimizer Engine Orchestrator.
"""

from codeslim.llm.models import LLMRefactorResponse, RefactorAction
from codeslim.optimizer.engine import OptimizerEngine


def test_optimizer_engine_valid_refactoring():
    original = "def hello():\n    print('hi')\n\ndef unused():\n    pass\n"
    optimized = "def hello():\n    print('hello world')\n\ndef unused():\n    pass\n"

    response = LLMRefactorResponse(
        summary="Improved greeting",
        actions=[
            RefactorAction(
                action_type="simplify_complexity",
                target_symbol="hello",
                line_start=1,
                line_end=2,
                explanation="Better greeting",
            )
        ],
        optimized_code=optimized,
        confidence_score=0.9,
    )

    engine = OptimizerEngine()
    result = engine.optimize(original, response, file_path="test.py")

    assert result["validation_passed"] is True
    assert result["error_message"] is None
    assert result["optimized_code"] == optimized
    assert len(result["diff"]) > 0
    assert result["confidence_tiers"]["suggest"] != []


def test_optimizer_engine_rejects_syntax_error():
    original = "def hello():\n    pass\n"
    broken_code = "def hello(\n    pass\n"

    response = LLMRefactorResponse(
        summary="Broken refactoring",
        actions=[],
        optimized_code=broken_code,
        confidence_score=0.5,
    )

    engine = OptimizerEngine()
    result = engine.optimize(original, response)

    assert result["validation_passed"] is False
    assert "Syntax error" in result["error_message"]
    assert result["optimized_code"] == original  # Falls back to original


def test_optimizer_engine_rejects_missing_signature():
    original = "def keep():\n    pass\n\ndef remove():\n    pass\n"
    optimized = "def keep():\n    pass\n"

    response = LLMRefactorResponse(
        summary="Accidentally removed function",
        actions=[],
        optimized_code=optimized,
        confidence_score=0.8,
    )

    engine = OptimizerEngine()
    result = engine.optimize(original, response)

    assert result["validation_passed"] is False
    assert "remove" in result["missing_signatures"]
    assert result["optimized_code"] == original  # Falls back to original
