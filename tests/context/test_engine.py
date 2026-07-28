"""
Unit tests for Context Engine and Bloat Score Aggregation.
"""

from codeslim.context.engine import ContextEngine, calculate_bloat_score
from codeslim.models.metrics import DeadCodeItem, FileMetrics, FunctionMetrics


def test_calculate_bloat_score_empty():
    score = calculate_bloat_score({"functions": [], "dead_code": [], "max_nesting_depth": 0})
    assert score == 0.0


def test_calculate_bloat_score_scalar_aggregation_fixes_bug_11():
    metrics = FileMetrics(
        file_path="sample.py",
        total_lines=100,
        functions=[
            FunctionMetrics(name="func1", line_start=1, line_end=10, cyclomatic_complexity=5),
            FunctionMetrics(name="func2", line_start=11, line_end=30, cyclomatic_complexity=15),
        ],
        dead_code=[
            DeadCodeItem(name="unused_var", line=5, code_type="variable", confidence=90, message="unused"),
        ],
    )
    score = calculate_bloat_score(metrics)
    assert 0.0 < score <= 1.0


def test_context_engine_minimization_pipeline(tmp_path):
    sample_file = tmp_path / "bloated.py"
    source = '''
"""Verbose module docstring."""

def compute():
    """Verbose function docstring."""
    unused_x = 10
    return 42
'''
    sample_file.write_text(source, encoding="utf-8")

    engine = ContextEngine(max_token_budget=1000)
    result = engine.minimize_context(
        file_path=sample_file,
        raw_code=source,
        file_metrics={
            "functions": [{"name": "compute", "line_start": 4, "line_end": 7, "cyclomatic_complexity": 2}],
            "dead_code": [
                {
                    "name": "unused_x",
                    "line": 6,
                    "code_type": "variable",
                    "confidence": 90,
                    "message": "unused",
                }
            ],
            "max_nesting_depth": 1,
        },
    )

    assert "bloat_score" in result
    assert result["tokens_saved"] >= 0
    assert "Verbose module docstring" not in result["pruned_code"]
    assert "You are CodeSlim's Agentic Refactoring Engine" in result["system_prompt"]
    assert "[Pruned Python Source Code]" in result["user_prompt"]
