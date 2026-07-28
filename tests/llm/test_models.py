"""
Unit tests for LLM Response Schemas.
"""

import pytest
from pydantic import ValidationError

from codeslim.llm.models import LLMRefactorResponse, RefactorAction


def test_refactor_action_valid():
    action = RefactorAction(
        action_type="remove_dead_code",
        target_symbol="unused_func",
        line_start=10,
        line_end=15,
        explanation="Unused helper function",
    )
    assert action.action_type == "remove_dead_code"
    assert action.line_start == 10


def test_refactor_response_valid():
    response = LLMRefactorResponse(
        summary="Removed dead code and simplified loop",
        actions=[
            RefactorAction(
                action_type="remove_dead_code",
                target_symbol="old_var",
                line_start=5,
                line_end=5,
                explanation="Dead assignment",
            )
        ],
        optimized_code="def main(): pass",
        confidence_score=0.95,
    )
    assert len(response.actions) == 1
    assert response.confidence_score == 0.95


def test_refactor_action_invalid_type():
    with pytest.raises(ValidationError):
        RefactorAction(
            action_type="remove_dead_code",
            target_symbol="foo",
            line_start=-5,  # Must be >= 1
            line_end=2,
            explanation="Test",
        )
