"""
Unit tests for data merging in analyze_node (RC-4 & RC-5 fixes).
"""

from pathlib import Path

from codeslim.pipeline.nodes import analyze_node


def test_analyze_node_merges_cognitive_complexity_and_imports(tmp_path: Path):
    test_file = tmp_path / "sample_analysis.py"
    raw_code = """import os
import sys

def complex_func(a, b):
    if a > 0:
        if b > 0:
            return a + b
    return 0
"""
    test_file.write_text(raw_code, encoding="utf-8")

    state = {
        "file_path": test_file,
        "stages_completed": [],
        "errors": [],
    }

    result_state = analyze_node(state)

    assert "analyze" in result_state["stages_completed"]
    file_metrics = result_state["file_metrics"]

    # Verify total_imports (RC-5 fix)
    assert file_metrics.total_imports == 2

    # Verify cognitive complexity merging (RC-4 fix)
    func_names = [f.name for f in file_metrics.functions]
    assert "complex_func" in func_names
    complex_fn = next(f for f in file_metrics.functions if f.name == "complex_func")
    assert complex_fn.cognitive_complexity > 0
