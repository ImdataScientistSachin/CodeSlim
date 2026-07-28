"""
Unit tests for Node 2.5 Deterministic Fix Node.
"""

from pathlib import Path

from codeslim.models.metrics import DeadCodeItem, FileMetrics
from codeslim.pipeline.nodes import deterministic_fix_node


def test_deterministic_fix_node_removes_unused_imports(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    raw_code = "import os\nimport unused_package\n\ndef main():\n    print(os.name)\n"
    test_file.write_text(raw_code)

    file_metrics = FileMetrics(
        file_path=str(test_file),
        total_lines=5,
        dead_code=[
            DeadCodeItem(name="unused_package", line=2, code_type="import", confidence=100)
        ],
    )

    state = {
        "file_path": test_file,
        "raw_code": raw_code,
        "file_metrics": file_metrics,
        "stages_completed": [],
    }

    new_state = deterministic_fix_node(state)

    assert "deterministic_fix" in new_state["stages_completed"]
    assert "unused_package" not in new_state["optimized_code"]
    assert "import os" in new_state["optimized_code"]
    assert new_state["deterministic_fixes_applied"] > 0


def test_deterministic_fix_node_no_dead_code(tmp_path: Path):
    test_file = tmp_path / "sample.py"
    raw_code = "import os\n\ndef main():\n    print(os.name)\n"
    test_file.write_text(raw_code)

    file_metrics = FileMetrics(file_path=str(test_file), total_lines=4)

    state = {
        "file_path": test_file,
        "raw_code": raw_code,
        "file_metrics": file_metrics,
        "stages_completed": [],
    }

    new_state = deterministic_fix_node(state)

    assert new_state["deterministic_fixes_applied"] == 0
    assert "deterministic_fix" not in new_state["stages_completed"]
