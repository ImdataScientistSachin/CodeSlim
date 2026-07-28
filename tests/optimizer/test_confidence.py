"""
Unit tests for 3-Tier Confidence Classifier.
"""

from typing import Literal

from codeslim.llm.models import RefactorAction
from codeslim.optimizer.confidence import classify_refactoring_actions

ActionType = Literal["remove_dead_code", "simplify_complexity", "inline_variable", "extract_function"]


def _make_action(action_type: ActionType) -> RefactorAction:
    return RefactorAction(
        action_type=action_type,
        target_symbol="test_symbol",
        line_start=1,
        line_end=5,
        explanation="Test explanation",
    )


def test_classify_auto_safe():
    actions = [_make_action("remove_dead_code")]
    tiers = classify_refactoring_actions(actions)
    assert len(tiers.auto_safe) == 1
    assert len(tiers.suggest) == 0
    assert len(tiers.flag_only) == 0


def test_classify_suggest():
    actions = [_make_action("simplify_complexity"), _make_action("inline_variable")]
    tiers = classify_refactoring_actions(actions)
    assert len(tiers.auto_safe) == 0
    assert len(tiers.suggest) == 2
    assert len(tiers.flag_only) == 0


def test_classify_flag_only():
    actions = [_make_action("extract_function")]
    tiers = classify_refactoring_actions(actions)
    assert len(tiers.auto_safe) == 0
    assert len(tiers.suggest) == 0
    assert len(tiers.flag_only) == 1


def test_classify_mixed_tiers():
    actions = [
        _make_action("remove_dead_code"),
        _make_action("simplify_complexity"),
        _make_action("extract_function"),
    ]
    tiers = classify_refactoring_actions(actions)
    assert len(tiers.auto_safe) == 1
    assert len(tiers.suggest) == 1
    assert len(tiers.flag_only) == 1
