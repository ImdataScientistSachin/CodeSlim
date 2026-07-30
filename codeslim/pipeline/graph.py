"""
LangGraph StateGraph Engine for CodeSlim.

Orchestrates parallel sensor dispatch, context minimization, bloat score threshold
routing, chunked LLM refactoring, ASTInvariantGate safety verification, and
Reflective Critic repair loops.
"""

from __future__ import annotations

import asyncio
import multiprocessing
import operator
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Annotated, Any, Literal, TypedDict, cast

from langgraph.graph import END, START, StateGraph

from codeslim.analyzers.ast_analyzer import ASTAnalyzer
from codeslim.analyzers.cognitive import CognitiveAnalyzer
from codeslim.analyzers.complexity import ComplexityAnalyzer
from codeslim.analyzers.dead_code import DeadCodeAnalyzer
from codeslim.analyzers.duplication import DuplicationAnalyzer
from codeslim.analyzers.tree_sitter_sensor import TreeSitterSensor
from codeslim.context.docstring_compressor import DocstringCompressor
from codeslim.context.engine import calculate_bloat_score
from codeslim.context.pruner import prune_source_code, remove_unused_imports
from codeslim.models.metrics import FileMetrics
from codeslim.optimizer.ast_guard import ASTInvariantGate
from codeslim.optimizer.diff_generator import generate_unified_diff
from codeslim.utils.logger import get_logger

logger = get_logger(__name__)


# ── Custom State Reducer Strategy (v5 Audit Verification) ────────────────────

def merge_sensor_results(current: dict[str, Any] | None, new: dict[str, Any] | None) -> dict[str, Any]:
    """Custom dictionary-merge reducer preventing last-write-wins overwrites
    and avoiding TypeError from operator.add on dictionaries.
    """
    merged = dict(current or {})
    if new:
        merged.update(new)
    return merged


class PipelineState(TypedDict, total=False):
    """LangGraph state schema for CodeSlim execution graph."""

    target_path: str
    raw_code: str
    no_llm: bool
    # Custom dict-merge reducer for parallel sensor outputs
    sensor_results: Annotated[dict[str, Any], merge_sensor_results]
    file_metrics: FileMetrics | None
    pruned_code: str | None
    bloat_score: float
    tokens_saved: int
    optimized_code: str | None
    unified_diff: str | None
    confidence_tiers: dict[str, Any] | None
    # List append reducer for AST error trace tracking across critic retries
    ast_errors: Annotated[list[str], operator.add]
    retry_count: int
    validation_passed: bool
    stages_completed: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]


# ── Picklable Module-Level Process Workers (CPython spawn GIL Bypass) ───────

def _run_radon_worker(target_path_str: str) -> dict[str, Any]:
    """Top-level worker for Radon Cyclomatic Complexity (picklable under spawn)."""
    analyzer = ComplexityAnalyzer()
    return {"complexity": analyzer.analyze(Path(target_path_str))}


def _run_vulture_worker(target_path_str: str) -> dict[str, Any]:
    """Top-level worker for Vulture Dead Code scanning (picklable under spawn)."""
    analyzer = DeadCodeAnalyzer()
    return {"dead_code": analyzer.analyze(Path(target_path_str))}


def _run_lizard_worker(target_path_str: str) -> dict[str, Any]:
    """Top-level worker for Lizard Cognitive Complexity scanning (picklable under spawn)."""
    analyzer = CognitiveAnalyzer()
    return {"cognitive": analyzer.analyze(Path(target_path_str))}


# ── StateGraph Node Implementations ──────────────────────────────────────────

async def parallel_sensor_node(state: PipelineState) -> dict[str, Any]:
    """Runs static code sensors in parallel.

    Uses ProcessPoolExecutor with 'spawn' context for pure-Python tools (GIL bypass)
    and asyncio.to_thread for C-native extensions (Tree-Sitter).
    """
    target_path_str = state["target_path"]
    target_path = Path(target_path_str)

    loop = asyncio.get_running_loop()
    spawn_ctx = multiprocessing.get_context("spawn")

    # CPU-bound pure-Python tools run via ProcessPoolExecutor (spawn context)
    with ProcessPoolExecutor(max_workers=3, mp_context=spawn_ctx) as executor:
        radon_fut = loop.run_in_executor(executor, _run_radon_worker, target_path_str)
        vulture_fut = loop.run_in_executor(executor, _run_vulture_worker, target_path_str)
        lizard_fut = loop.run_in_executor(executor, _run_lizard_worker, target_path_str)

        # C-extension Tree-Sitter & stdlib AST run via asyncio.to_thread
        ts_fut = asyncio.to_thread(TreeSitterSensor().extract_skeleton, state["raw_code"])
        ast_fut = asyncio.to_thread(ASTAnalyzer().analyze, target_path)
        duplication_fut = asyncio.to_thread(DuplicationAnalyzer().analyze, target_path)

        results = await asyncio.gather(
            radon_fut, vulture_fut, lizard_fut, ts_fut, ast_fut, duplication_fut
        )

    radon_res, vulture_res, lizard_res, ts_res, ast_res, dup_res = results

    # Construct unified FileMetrics
    complexity_data = radon_res.get("complexity", {})
    dead_code_data = vulture_res.get("dead_code", {})
    cognitive_data = lizard_res.get("cognitive", {})

    functions = complexity_data.get("functions", [])
    dead_items = dead_code_data.get("dead_code", [])
    cognitive_metrics = cognitive_data.get("all_functions", [])

    fn_map = {fn.name: fn for fn in functions}
    for cog_fn in cognitive_metrics:
        fn_name = cog_fn.get("name")
        if fn_name and fn_name in fn_map:
            fn_map[fn_name].cognitive_complexity = cog_fn.get("cognitive_complexity", 0)

    total_lines = len(state["raw_code"].splitlines())
    duplication_ratio = dup_res.get("duplication_ratio", 0.0)
    all_imports = ast_res.get("all_imports", [])

    file_metrics = FileMetrics(
        file_path=str(target_path),
        total_lines=total_lines,
        functions=list(fn_map.values()),
        dead_code=dead_items,
        total_imports=len(all_imports),
        third_party_imports=ast_res.get("third_party_imports", []),
        stdlib_imports=ast_res.get("stdlib_imports", []),
        duplication_ratio=duplication_ratio,
    )

    sensor_dict = {
        "file_metrics": file_metrics,
        "tree_sitter": ts_res,
        "duplication": dup_res,
    }

    return {
        "sensor_results": sensor_dict,
        "file_metrics": file_metrics,
        "stages_completed": ["analyze"],
    }


async def minimizer_node(state: PipelineState) -> dict[str, Any]:
    """Prunes dead code & compresses docstrings via LibCST + TF-IDF DocstringCompressor."""
    raw_code = state["raw_code"]
    file_metrics = state.get("file_metrics")

    dead_lines = set()
    if file_metrics:
        dead_lines = {item.line for item in file_metrics.dead_code if item.confidence >= 80}

    # Step 1: Lossless LibCST pruning
    pruned = prune_source_code(raw_code, dead_code_lines=dead_lines, strip_docstrings=True)

    # Step 2: NLTK TF-IDF Docstring compression
    pruned = DocstringCompressor().compress_code_docstrings(pruned)

    # Calculate Bloat Score
    bloat_score = calculate_bloat_score(file_metrics) if file_metrics else 0.0
    tokens_saved = len(raw_code) - len(pruned)

    return {
        "pruned_code": pruned,
        "bloat_score": bloat_score,
        "tokens_saved": max(0, tokens_saved),
        "stages_completed": ["minimize"],
    }


async def deterministic_fix_node(state: PipelineState) -> dict[str, Any]:
    """Node 2.5 — Purges unused imports deterministically with LibCST (0% LLM cost)."""
    raw_code = state["raw_code"]
    file_metrics = state.get("file_metrics")

    unused_imports = set()
    if file_metrics:
        unused_imports = {
            item.name for item in file_metrics.dead_code
            if item.code_type == "import" and item.confidence >= 80
        }

    fixed_code = remove_unused_imports(raw_code, unused_imports)
    diff = generate_unified_diff(raw_code, fixed_code, state["target_path"])

    return {
        "optimized_code": fixed_code,
        "unified_diff": diff,
        "validation_passed": True,
        "stages_completed": ["deterministic_fix"],
    }


async def llm_refactor_node(state: PipelineState) -> dict[str, Any]:
    """Calls LLM provider for chunked guard clause refactoring."""
    from codeslim.context.prompts import SYSTEM_ANALYSIS_PROMPT, build_user_prompt
    from codeslim.llm.client import LLMClient

    raw_code = state["raw_code"]
    pruned_code = state.get("pruned_code") or raw_code
    file_metrics = state.get("file_metrics")

    max_cc = file_metrics.max_cyclomatic_complexity if file_metrics else 0
    dead_count = len(file_metrics.dead_code) if file_metrics else 0

    user_prompt = build_user_prompt(
        file_name=Path(state["target_path"]).name,
        bloat_score=state.get("bloat_score", 0.0),
        max_cc=max_cc,
        dead_code_count=dead_count,
        pruned_code=pruned_code,
    )

    # Check if this is a reflective retry attempt
    ast_errors = state.get("ast_errors", [])
    if ast_errors and state.get("retry_count", 0) > 0:
        latest_error = ast_errors[-1]
        user_prompt += (
            f"\n\n[CRITICAL CORRECTION REQUIRED - RETRY ATTEMPT {state['retry_count']}]\n"
            f"Your previous refactored code was rejected by the AST Safety Gate because:\n"
            f"--> {latest_error}\n"
            f"Fix this error immediately! Preserve all public function/class headers and decorators."
        )

    client = LLMClient()
    try:
        completion = await client.invoke(system_prompt=SYSTEM_ANALYSIS_PROMPT, user_prompt=user_prompt)
        # Handle JSON extraction
        import json
        import re
        json_match = re.search(r"\{.*\}", completion, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            opt_code = data.get("optimized_code", pruned_code)
        else:
            opt_code = pruned_code
    except Exception as ex:
        logger.warning("llm_refactor_failed", error=str(ex))
        opt_code = pruned_code

    return {
        "optimized_code": opt_code,
        "stages_completed": ["llm_refactor"],
    }


async def guardrail_node(state: PipelineState) -> dict[str, Any]:
    """Validates refactored code against AST Invariants."""
    raw_code = state["raw_code"]
    optimized_code = state.get("optimized_code") or raw_code

    gate = ASTInvariantGate()
    if gate.is_safe(raw_code, optimized_code):
        diff = generate_unified_diff(raw_code, optimized_code, state["target_path"])
        return {
            "validation_passed": True,
            "unified_diff": diff,
            "stages_completed": ["guardrails"],
        }

    return {
        "validation_passed": False,
        "ast_errors": ["AST invariant failure: public signature or decorator mutated by LLM"],
        "stages_completed": ["guardrails"],
    }


async def report_node(state: PipelineState) -> dict[str, Any]:
    """Assembles final report model and returns populated state."""
    return {
        "stages_completed": ["report"],
    }


# ── Conditional Routing Edges ────────────────────────────────────────────────

def route_after_minimizer(state: PipelineState) -> Literal["deterministic_fix_node", "llm_refactor_node", "report_node"]:
    """Conditional Edge 1: Routes based on bloat score and --no-llm flag."""
    if state.get("no_llm", False):
        return "deterministic_fix_node"

    bloat_score = state.get("bloat_score", 0.0)
    file_metrics = state.get("file_metrics")
    max_cc = file_metrics.max_cyclomatic_complexity if file_metrics else 0

    if bloat_score < 5.0 and max_cc <= 10:
        # Fast exit — clean code (0 LLM cost)
        return "report_node"
    elif max_cc <= 10 and file_metrics and len(file_metrics.dead_code) > 0:
        # Dead code only — Node 2.5 deterministic fix (0 LLM cost)
        return "deterministic_fix_node"
    else:
        # Complex logic — LLM refactoring required
        return "llm_refactor_node"


def route_after_guardrail(state: PipelineState) -> Literal["report_node", "critic_node", "deterministic_fix_node"]:
    """Conditional Edge 2: Routes after AST Guardrail check."""
    if state.get("validation_passed", False):
        return "report_node"

    retry_count = state.get("retry_count", 0)
    if retry_count < 2:
        return "critic_node"

    # Retries exceeded — fallback to Node 2.5 (Deterministic LibCST Fix)
    logger.warning("critic_retries_exceeded_fallback_to_node_2_5")
    return "deterministic_fix_node"


# ── StateGraph Construction & Compilation ───────────────────────────────────

builder = StateGraph(cast(Any, PipelineState))

# Add Nodes
builder.add_node("parallel_sensor_node", parallel_sensor_node)
builder.add_node("minimizer_node", minimizer_node)
builder.add_node("deterministic_fix_node", deterministic_fix_node)
builder.add_node("llm_refactor_node", llm_refactor_node)
builder.add_node("guardrail_node", guardrail_node)
builder.add_node("report_node", report_node)

# Delayed import for critic_node to avoid circular import
async def _critic_node_wrapper(state: PipelineState) -> dict[str, Any]:
    from codeslim.pipeline.critic import reflective_critic_node
    return await reflective_critic_node(state)

builder.add_node("critic_node", _critic_node_wrapper)

# Add Edges
builder.add_edge(START, "parallel_sensor_node")
builder.add_edge("parallel_sensor_node", "minimizer_node")

# Conditional Edge 1 (after minimizer)
builder.add_conditional_edges(
    "minimizer_node",
    route_after_minimizer,
    {
        "deterministic_fix_node": "deterministic_fix_node",
        "llm_refactor_node": "llm_refactor_node",
        "report_node": "report_node",
    },
)

builder.add_edge("llm_refactor_node", "guardrail_node")

# Conditional Edge 2 (after guardrail)
builder.add_conditional_edges(
    "guardrail_node",
    route_after_guardrail,
    {
        "report_node": "report_node",
        "critic_node": "critic_node",
        "deterministic_fix_node": "deterministic_fix_node",
    },
)

builder.add_edge("critic_node", "llm_refactor_node")
builder.add_edge("deterministic_fix_node", "report_node")
builder.add_edge("report_node", END)

# Module-level compiled graph singleton
compiled_graph = builder.compile()
