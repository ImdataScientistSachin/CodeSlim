"""
CodeSlim Performance & Latency Benchmark Suite.

Benchmarks:
1. ASTAnalyzer & Static Complexity Sensors (Radon/Lizard)
2. CST Lossless Minimizer
3. AST Invariant Gate
4. End-to-End Local Orchestrator Throughput
"""

import pathlib
import sys
import time

# Ensure project root in pythonpath
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# Windows UTF-8 stdout handling
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from codeslim.context.pruner import remove_dead_functions, remove_unused_imports  # noqa: E402
from codeslim.optimizer.ast_guard import ASTInvariantGate  # noqa: E402
from codeslim.pipeline.project_orchestrator import ProjectOrchestrator  # noqa: E402

SAMPLE_BLOATED_CODE = '''
import os
import sys
import json
import pd_utils  # Unused fake import
from typing import Optional, List, Dict

# Unused helper constant
UNUSED_CONSTANT = "bloat"

def process_data(payload: dict) -> Optional[dict]:
    """Process payload with unnecessary defensive nesting."""
    result = None
    if payload:
        if isinstance(payload, dict):
            if "data" in payload:
                if payload["data"]:
                    if len(payload["data"]) > 0:
                        raw = payload["data"]
                        for item in raw:
                            if item:
                                if "id" in item:
                                    result = {"status": "ok", "id": item["id"]}
    return result

def dead_function():
    """Unused function that should be pruned."""
    x = 10
    y = 20
    return x + y
'''


def run_benchmarks() -> None:
    print("==========================================================")
    print("          CodeSlim Benchmark Suite (Local Surgery)        ")
    print("==========================================================")

    import ast

    from radon.complexity import cc_visit

    start_t = time.perf_counter()
    iterations = 50
    for _ in range(iterations):
        _ = ast.parse(SAMPLE_BLOATED_CODE)
        _ = cc_visit(SAMPLE_BLOATED_CODE)
    elapsed_sensor = (time.perf_counter() - start_t) / iterations * 1000

    print(f"[1] Static Sensors (AST + Radon CC):   {elapsed_sensor:.2f} ms / run")

    # 2. Benchmark LibCST Lossless Minimizer
    start_t = time.perf_counter()
    for _ in range(iterations):
        cleaned_imports = remove_unused_imports(SAMPLE_BLOATED_CODE, {"pd_utils"})
        optimized_code = remove_dead_functions(cleaned_imports, {"dead_function"})
    elapsed_cst = (time.perf_counter() - start_t) / iterations * 1000

    orig_tokens = len(SAMPLE_BLOATED_CODE.split())
    opt_tokens = len(optimized_code.split())
    token_reduc = (orig_tokens - opt_tokens) / orig_tokens * 100
    print(f"[2] LibCST Minimizer:                   {elapsed_cst:.2f} ms / run ({token_reduc:.1f}% token reduction)")

    # 3. Benchmark AST Invariant Gate
    gate = ASTInvariantGate()
    start_t = time.perf_counter()
    for _ in range(iterations):
        _ = gate.validate(SAMPLE_BLOATED_CODE, optimized_code)
    elapsed_gate = (time.perf_counter() - start_t) / iterations * 1000

    print(f"[3] AST Invariant Safety Gate:         {elapsed_gate:.2f} ms / run")

    # 4. End-to-End Deterministic Pipeline (Zero LLM cost)
    demo_file = PROJECT_ROOT / "examples" / "Demo_test_bloated.py"
    orchestrator = ProjectOrchestrator()
    start_t = time.perf_counter()
    iterations_e2e = 5
    for _ in range(iterations_e2e):
        proj_report = orchestrator.scan_directory(str(demo_file), no_llm=True)
    elapsed_pipeline = (time.perf_counter() - start_t) / iterations_e2e * 1000

    print(f"[4] Full Deterministic Pipeline Run:   {elapsed_pipeline:.2f} ms / run (312-line test file)")
    print("----------------------------------------------------------")
    if proj_report.file_reports:
        file_rep = proj_report.file_reports[0]
        print(f"Summary: Bloat Score: {file_rep.bloat_score:.1f}/100 | Grade: {file_rep.bloat_grade}")
        print(f"Lines Saved: {file_rep.lines_saved} | Reduction: {file_rep.reduction_percentage}% | AST Safe: {file_rep.validation_passed}")
    print("==========================================================")


if __name__ == "__main__":
    run_benchmarks()
