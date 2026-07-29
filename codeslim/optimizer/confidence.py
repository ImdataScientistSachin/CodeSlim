"""
3-Tier Confidence Classifier for CodeSlim.

Categorizes LLM-proposed refactoring actions into Auto-Safe,
Suggest, and Flag-Only tiers based on action risk level.
"""

from codeslim.llm.models import RefactorAction
from codeslim.models.report import ConfidenceTiers
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.optimizer.confidence")

# Tier mapping: action_type -> confidence tier
_TIER_MAP: dict[str, str] = {
    "remove_dead_code": "auto_safe",
    "inline_variable": "suggest",
    "simplify_complexity": "suggest",
    "consolidate_classes": "suggest",
    "extract_function": "flag_only",
}


def classify_refactoring_actions(
    actions: list[RefactorAction],
) -> ConfidenceTiers:
    """
    Classify refactoring actions into 3 confidence tiers.

    Tier 1 (auto_safe): Dead code removal — safe to auto-apply.
    Tier 2 (suggest): Simplification, inlining — needs developer review.
    Tier 3 (flag_only): Structural extraction — manual review required.

    Args:
        actions: List of RefactorAction objects from LLM response.

    Returns:
        ConfidenceTiers with categorized action dictionaries.
    """
    tiers = ConfidenceTiers()

    for action in actions:
        action_dict = action.model_dump()
        tier = _TIER_MAP.get(action.action_type, "flag_only")

        if tier == "auto_safe":
            tiers.auto_safe.append(action_dict)
        elif tier == "suggest":
            tiers.suggest.append(action_dict)
        else:
            tiers.flag_only.append(action_dict)

    log.info(
        "confidence_classification_complete",
        auto_safe=len(tiers.auto_safe),
        suggest=len(tiers.suggest),
        flag_only=len(tiers.flag_only),
    )

    return tiers
