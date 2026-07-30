"""
Unit tests for LangGraph StateGraph Engine & Reflective Critic Repair Loops.
"""

import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pytest

from codeslim.pipeline.critic import reflective_critic_node
from codeslim.pipeline.graph import (
    PipelineState,
    _run_lizard_worker,
    _run_radon_worker,
    _run_vulture_worker,
    compiled_graph,
    merge_sensor_results,
    route_after_guardrail,
    route_after_minimizer,
)


def test_spawn_process_pool_workers_picklable(tmp_path: Path):
    """Verifies that top-level sensor workers pickle cleanly under CPython spawn context."""
    test_file = tmp_path / "sample.py"
    test_file.write_text("def hello():\n    print('world')\n")

    spawn_ctx = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=3, mp_context=spawn_ctx) as executor:
        radon_fut = executor.submit(_run_radon_worker, str(test_file))
        vulture_fut = executor.submit(_run_vulture_worker, str(test_file))
        lizard_fut = executor.submit(_run_lizard_worker, str(test_file))

        radon_res = radon_fut.result()
        vulture_res = vulture_fut.result()
        lizard_res = lizard_fut.result()

    assert "complexity" in radon_res
    assert "dead_code" in vulture_res
    assert "cognitive" in lizard_res


def test_merge_sensor_results_reducer():
    """Verifies custom dict-merge reducer prevents TypeError and merges keys safely."""
    curr = {"radon": {"max_cc": 12}}
    new = {"vulture": {"dead_count": 2}}

    merged = merge_sensor_results(curr, new)
    assert merged == {"radon": {"max_cc": 12}, "vulture": {"dead_count": 2}}

    # Verify None handling
    assert merge_sensor_results(None, new) == new
    assert merge_sensor_results(curr, None) == curr


def test_route_after_minimizer():
    """Verifies conditional edge routing logic after minimizer node."""
    # Fast exit for no_llm
    state_no_llm: PipelineState = {"no_llm": True, "bloat_score": 15.0}
    assert route_after_minimizer(state_no_llm) == "deterministic_fix_node"

    # Fast exit for clean code
    state_clean: PipelineState = {"no_llm": False, "bloat_score": 2.0}
    assert route_after_minimizer(state_clean) == "report_node"


def test_route_after_guardrail():
    """Verifies conditional edge routing after guardrail check."""
    # Validation passed
    state_pass: PipelineState = {"validation_passed": True}
    assert route_after_guardrail(state_pass) == "report_node"

    # Validation failed, retries available -> critic
    state_retry: PipelineState = {"validation_passed": False, "retry_count": 0}
    assert route_after_guardrail(state_retry) == "critic_node"

    # Validation failed, max retries exceeded -> fallback to deterministic fix
    state_fallback: PipelineState = {"validation_passed": False, "retry_count": 2}
    assert route_after_guardrail(state_fallback) == "deterministic_fix_node"


@pytest.mark.asyncio
async def test_reflective_critic_node():
    """Verifies reflective critic node increments retry counter."""
    state: PipelineState = {
        "retry_count": 0,
        "ast_errors": ["missing_signature: func_a deleted by LLM"],
    }
    update = await reflective_critic_node(state)
    assert update["retry_count"] == 1


@pytest.mark.asyncio
async def test_compiled_graph_end_to_end(tmp_path: Path):
    """Verifies end-to-end execution of compiled StateGraph on a python file."""
    test_file = tmp_path / "test_script.py"
    test_file.write_text(
        "import sys\nimport os\n\ndef calculate(x):\n    if x > 0:\n        return x * 2\n    return 0\n"
    )

    initial_state = {
        "target_path": str(test_file.resolve()),
        "raw_code": test_file.read_text(),
        "no_llm": True,
        "retry_count": 0,
        "sensor_results": {},
        "ast_errors": [],
        "stages_completed": [],
        "errors": [],
    }

    final_state = await compiled_graph.ainvoke(initial_state)
    assert "analyze" in final_state["stages_completed"]
    assert "minimize" in final_state["stages_completed"]
    assert final_state.get("file_metrics") is not None
