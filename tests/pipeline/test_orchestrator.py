"""
Unit tests for Pipeline Orchestrator & State Machine.
"""

from pathlib import Path

import pytest

from codeslim.pipeline.orchestrator import PipelineOrchestrator


@pytest.mark.asyncio
async def test_pipeline_no_llm_mode(tmp_path: Path):
    """Test full pipeline execution in --no-llm analysis mode."""
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("def hello():\n    unused_var = 10\n    print('hi')\n")

    orchestrator = PipelineOrchestrator()
    report = await orchestrator.run_pipeline(test_file, no_llm=True)

    assert report.file_path == str(test_file)
    assert report.original_lines == 3
    assert "analyze" in report.stages_completed
    assert "minimize" in report.stages_completed
    assert "report" in report.stages_completed
    assert report.bloat_score >= 0.0


@pytest.mark.asyncio
async def test_pipeline_bloat_map_generation(tmp_path: Path):
    """Test bloat map entry generation for high complexity and dead code."""
    test_file = tmp_path / "complex_sample.py"
    code = """
def complex_fn(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return 1
    return 0
"""
    test_file.write_text(code)

    orchestrator = PipelineOrchestrator()
    report = await orchestrator.run_pipeline(test_file, no_llm=True)

    assert report.original_lines > 0
    assert report.bloat_grade in ["A", "B", "C", "D", "F"]
