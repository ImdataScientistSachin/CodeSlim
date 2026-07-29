"""
Pipeline State Machine Nodes for CodeSlim.

Defines isolated, pure execution nodes for state graph routing:
Node 1: Analyze Node (Radon, Vulture, Lizard, AST, Duplication)
Node 2: Minimize Node (LibCST Token Pruner)
Node 2.5: Deterministic Fix Node (LibCST Auto-Apply Dead Imports & Variables)
Node 3: LLM Refactor Node (Function-Level Chunked LLM Generation)
Node 4: Guardrail Node (AST Validation & Diff Generation)
Node 5: Report Assembly Node (Final Pydantic Report Generation)
"""

import ast
from pathlib import Path
from typing import Any

from codeslim.analyzers.ast_analyzer import ASTAnalyzer
from codeslim.analyzers.cognitive import CognitiveAnalyzer
from codeslim.analyzers.complexity import ComplexityAnalyzer
from codeslim.analyzers.dead_code import DeadCodeAnalyzer
from codeslim.analyzers.duplication import DuplicationAnalyzer
from codeslim.context.engine import ContextEngine
from codeslim.context.pruner import remove_dead_functions, remove_unused_imports
from codeslim.llm.client import LLMClient
from codeslim.llm.models import LLMRefactorResponse, RefactorAction
from codeslim.models.metrics import FileMetrics
from codeslim.models.report import BloatMapEntry, CodeSlimReport
from codeslim.optimizer.diff_generator import generate_unified_diff
from codeslim.optimizer.engine import OptimizerEngine
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.pipeline.nodes")


def analyze_node(state: dict[str, Any]) -> dict[str, Any]:
    """Node 1: Execute all static analysis sensors concurrently."""
    file_path: Path = state["file_path"]
    log.info("executing_analyze_node", file=file_path.name)

    raw_code = file_path.read_text(encoding="utf-8")
    state["raw_code"] = raw_code

    if not raw_code.strip():
        log.info("empty_file_skipped", path=str(file_path))
        state["file_metrics"] = FileMetrics(file_path=str(file_path), total_lines=0)
        state["stages_completed"].append("analyze_skipped_empty")
        return state

    complexity_analyzer = ComplexityAnalyzer()
    dead_code_analyzer = DeadCodeAnalyzer()
    cognitive_analyzer = CognitiveAnalyzer()
    ast_analyzer = ASTAnalyzer()
    duplication_analyzer = DuplicationAnalyzer()

    comp_info = complexity_analyzer.analyze(file_path)
    dead_info = dead_code_analyzer.analyze(file_path)
    cog_info = cognitive_analyzer.analyze(file_path)
    ast_info = ast_analyzer.analyze(file_path)
    dup_info = duplication_analyzer.analyze(file_path)

    fn_metrics = comp_info.get("functions", [])
    dead_code_items = dead_info.get("dead_code", [])
    cognitive_metrics = cog_info.get("all_functions", [])

    fn_map = {fn.name: fn for fn in fn_metrics}
    for cog_fn in cognitive_metrics:
        fn_name = cog_fn.get("name")
        if fn_name and fn_name in fn_map:
            fn_map[fn_name].cognitive_complexity = cog_fn.get("cognitive_complexity", 0)

    total_lines = len(raw_code.splitlines())
    duplication_ratio = dup_info.get("duplication_ratio", 0.0)
    all_imports = ast_info.get("all_imports", [])

    file_metrics = FileMetrics(
        file_path=str(file_path),
        total_lines=total_lines,
        functions=list(fn_map.values()),
        dead_code=dead_code_items,
        total_imports=len(all_imports),
        third_party_imports=ast_info.get("third_party_imports", []),
        stdlib_imports=ast_info.get("stdlib_imports", []),
        duplication_ratio=duplication_ratio,
    )

    state["file_metrics"] = file_metrics
    state["stages_completed"].append("analyze")
    return state


def minimize_node(state: dict[str, Any]) -> dict[str, Any]:
    """Node 2: Execute LibCST token minimizer."""
    if "file_metrics" not in state or state["file_metrics"].total_lines == 0:
        state["pruned_code"] = state.get("raw_code", "")
        state["bloat_score"] = 0.0
        state["stages_completed"].append("minimize_skipped")
        return state

    file_metrics: FileMetrics = state["file_metrics"]
    raw_code: str = state["raw_code"]
    file_path: Path = state["file_path"]
    max_token_budget: int = state.get("max_token_budget", 4096)

    log.info("executing_minimize_node", file=file_path.name)

    engine = ContextEngine(max_token_budget=max_token_budget)
    result = engine.minimize_context(file_path, raw_code, file_metrics)

    state["pruned_code"] = result["pruned_code"]
    state["bloat_score"] = result["bloat_score"]
    state["original_tokens"] = result["original_tokens"]
    state["tokens_saved"] = result["tokens_saved"]
    state["system_prompt"] = result["system_prompt"]
    state["user_prompt"] = result["user_prompt"]
    state["stages_completed"].append("minimize")
    return state


def deterministic_fix_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Node 2.5: Apply zero-hallucination deterministic fixes via LibCST.
    """
    if "file_metrics" not in state or state["file_metrics"].total_lines == 0:
        state["deterministic_fixes_applied"] = 0
        return state

    file_metrics: FileMetrics = state["file_metrics"]
    raw_code: str = str(
        state.get("optimized_code") or state.get("pruned_code") or state.get("raw_code", "")
    )

    unused_imports_and_vars = {
        item.name
        for item in file_metrics.dead_code
        if item.code_type in ("import", "variable") and item.confidence >= 60
    }

    unused_functions = {
        item.name
        for item in file_metrics.dead_code
        if item.code_type == "function" and item.confidence >= 60
    }

    if not unused_imports_and_vars and not unused_functions:
        state["deterministic_fixes_applied"] = 0
        return state

    fixed_code = raw_code
    if unused_imports_and_vars:
        fixed_code = remove_unused_imports(fixed_code, unused_imports_and_vars)
    if unused_functions:
        fixed_code = remove_dead_functions(fixed_code, unused_functions)

    lines_removed = max(0, len(raw_code.splitlines()) - len(fixed_code.splitlines()))

    log.info(
        "deterministic_fixes_applied",
        removed_symbols=sorted(unused_imports_and_vars | unused_functions),
        lines_removed=lines_removed,
    )

    state["optimized_code"] = fixed_code
    state["deterministic_fixes_applied"] = lines_removed
    state["stages_completed"].append("deterministic_fix")
    return state


def _detect_over_abstracted_classes(code: str) -> list[dict[str, Any]]:
    """
    Detect over-abstracted class chains (sequential small classes with <= 3 methods).

    Returns list of dicts containing class details.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []

    small_classes = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            if len(methods) <= 3:
                end_line = getattr(node, "end_lineno", node.lineno)
                small_classes.append(
                    {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": end_line,
                        "method_count": len(methods),
                    }
                )

    if len(small_classes) >= 3:
        return small_classes
    return []


async def llm_refactor_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Node 3: Function-Level & Class Cluster Chunked LLM Reasoner.

    Targeted refactoring: Extracts functions with CC > 10 or Nesting > 4,
    plus over-abstracted class clusters, and refactors them via LLMClient.
    """
    if state.get("no_llm", False):
        log.info("skipping_llm_node_no_llm_flag")
        state["llm_response"] = None
        state["stages_completed"].append("llm_refactor_skipped")
        return state

    if "file_metrics" not in state or state["file_metrics"].total_lines == 0:
        state["llm_response"] = None
        state["stages_completed"].append("llm_refactor_skipped_empty")
        return state

    file_metrics: FileMetrics = state["file_metrics"]
    current_code: str = str(
        state.get("optimized_code") or state.get("pruned_code") or state.get("raw_code", "")
    )
    complex_functions = [
        fn for fn in file_metrics.functions if fn.cyclomatic_complexity > 10 or fn.nesting_depth > 4
    ]
    class_cluster = _detect_over_abstracted_classes(current_code)

    if not complex_functions and not class_cluster:
        log.info("no_complex_functions_or_class_clusters_to_refactor")
        state["llm_response"] = None
        state["stages_completed"].append("llm_refactor_no_complex_functions")
        return state

    llm_client = LLMClient()
    actions = []
    lines = current_code.splitlines()

    for fn in complex_functions:
        log.info("chunk_refactoring_function", function=fn.name, cc=fn.cyclomatic_complexity)
        fn_lines = lines[fn.line_start - 1 : fn.line_end]
        fn_code = "\n".join(fn_lines)

        refactored_fn = await llm_client.refactor_function_chunk(
            function_code=fn_code,
            function_name=fn.name,
            cc_score=fn.cyclomatic_complexity,
        )

        if refactored_fn and refactored_fn != fn_code:
            prefix = "\n".join(lines[: fn.line_start - 1])
            suffix = "\n".join(lines[fn.line_end :])
            current_code = f"{prefix}\n{refactored_fn}\n{suffix}".strip()

            actions.append(
                RefactorAction(
                    action_type="simplify_complexity",
                    target_symbol=fn.name,
                    line_start=fn.line_start,
                    line_end=fn.line_end,
                    explanation=f"Refactored complex control flow (CC={fn.cyclomatic_complexity}, Nesting={fn.nesting_depth}) using guard clauses",
                )
            )

    if class_cluster:
        cluster_names = [c["name"] for c in class_cluster]
        line_start = class_cluster[0]["line_start"]
        line_end = class_cluster[-1]["line_end"]
        actions.append(
            RefactorAction(
                action_type="consolidate_classes",
                target_symbol=", ".join(cluster_names),
                line_start=line_start,
                line_end=line_end,
                explanation=f"Identified over-abstracted class cluster ({len(cluster_names)} single-responsibility classes: {', '.join(cluster_names)})",
            )
        )

    response = LLMRefactorResponse(
        summary=f"Processed {len(actions)} refactoring targets using chunking engine",
        actions=actions,
        optimized_code=current_code,
        confidence_score=0.90,
    )

    state["llm_response"] = response
    state["stages_completed"].append("llm_refactor")
    return state


def guardrail_node(state: dict[str, Any]) -> dict[str, Any]:
    """
    Node 4: Execute AST syntax guardrail & diff generator.

    Always computes unified diff whenever optimized_code differs from raw_code,
    ensuring deterministic CST fixes (Node 2.5) and LLM refactorings (Node 3)
    are always visually rendered.
    """
    raw_code: str = state.get("raw_code", "")
    file_path: Path = state["file_path"]

    # Step 1: If LLM produced a response, validate it via OptimizerEngine
    if state.get("llm_response"):
        log.info("executing_guardrail_node", file=file_path.name)
        llm_response: LLMRefactorResponse = state["llm_response"]
        optimizer = OptimizerEngine()
        result = optimizer.optimize(raw_code, llm_response, file_path=file_path.name)

        if result["validation_passed"]:
            state["optimized_code"] = result["optimized_code"]
            state["diff"] = result["diff"]
            state["confidence_tiers"] = result["confidence_tiers"]
            state["validation_passed"] = True
            state["stages_completed"].append("guardrail")
            return state
        else:
            log.warning("guardrail_rejected_llm_code", error=result.get("error_message"))
            state["errors"].append(f"Guardrail rejection: {result.get('error_message')}")
            state["validation_passed"] = False
            # Fallback optimized_code to current code (which may include Node 2.5 deterministic fixes)

    # Step 2: Ensure diff is generated whenever optimized_code differs from raw_code
    current_opt = str(state.get("optimized_code") or raw_code)
    if current_opt != raw_code:
        state["diff"] = generate_unified_diff(raw_code, current_opt, file_path=file_path.name)
        state["optimized_code"] = current_opt
    else:
        state["diff"] = ""
        if "optimized_code" not in state:
            state["optimized_code"] = raw_code

    if "confidence_tiers" not in state:
        state["confidence_tiers"] = {}

    state["stages_completed"].append("guardrail")
    return state


def report_node(state: dict[str, Any]) -> dict[str, Any]:
    """Node 5: Assemble final CodeSlimReport model."""
    file_path: Path = state["file_path"]
    file_metrics: FileMetrics | None = state.get("file_metrics")

    raw_lines = len(state.get("raw_code", "").splitlines())
    opt_code = state.get("optimized_code", state.get("raw_code", ""))
    opt_lines = len(opt_code.splitlines()) if opt_code else raw_lines

    bloat_map = []
    if file_metrics:
        for item in file_metrics.dead_code:
            bloat_map.append(
                BloatMapEntry(
                    bloat_type="dead_code",
                    severity="high" if item.code_type == "import" else "medium",
                    line_start=item.line,
                    line_end=item.line,
                    explanation=f"Unused {item.code_type}: {item.name}",
                    suggestion=f"Remove unused {item.code_type} '{item.name}'",
                )
            )

        for fn in file_metrics.functions:
            if fn.cyclomatic_complexity > 10:
                bloat_map.append(
                    BloatMapEntry(
                        bloat_type="high_complexity",
                        severity="high",
                        line_start=fn.line_start,
                        line_end=fn.line_end,
                        explanation=f"High Cyclomatic Complexity ({fn.cyclomatic_complexity}) in '{fn.name}'",
                        suggestion="Refactor complex control flow using guard clauses and early returns",
                    )
                )

        if file_metrics.duplication_ratio > 0.10:
            dup_pct = round(file_metrics.duplication_ratio * 100, 1)
            bloat_map.append(
                BloatMapEntry(
                    bloat_type="duplication",
                    severity="high" if file_metrics.duplication_ratio > 0.25 else "medium",
                    line_start=1,
                    line_end=file_metrics.total_lines,
                    explanation=f"Code duplication detected: {dup_pct}% of file has copy-pasted blocks",
                    suggestion="Extract shared logic into a reusable helper function",
                )
            )

    state["stages_completed"].append("report")

    report = CodeSlimReport(
        file_path=str(file_path),
        bloat_score=state.get("bloat_score", 0.0) * 100.0,
        original_lines=raw_lines,
        optimized_lines=opt_lines if opt_lines != raw_lines else None,
        bloat_map=bloat_map,
        optimized_code=state.get("optimized_code"),
        diff=state.get("diff"),
        confidence_tiers=state.get("confidence_tiers", {}),
        metrics=file_metrics,
        errors=state.get("errors", []),
        stages_completed=state.get("stages_completed", []),
    )

    state["report"] = report
    return state
