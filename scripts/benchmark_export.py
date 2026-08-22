"""
Benchmark script: Measure HTML Observatory export time.

Compares async concurrent scan vs old serial scan.
Run with:  python scripts/benchmark_export.py
"""

import asyncio
import time
from pathlib import Path

from codeslim.pipeline.project_orchestrator import ProjectOrchestrator
from codeslim.formatters.html_exporter import generate_html_observatory_report

TARGET = str(Path(__file__).parent.parent / "codeslim")


async def bench_async() -> float:
    """Benchmark: new concurrent async scanner."""
    orch = ProjectOrchestrator()
    t0 = time.perf_counter()
    report = await orch.scan_directory_async(TARGET, no_llm=True)
    html = generate_html_observatory_report(report)
    elapsed = time.perf_counter() - t0
    print(f"[ASYNC] Concurrent:  {elapsed:.2f}s  ({report.total_files} files, {len(html):,} bytes HTML)")
    return elapsed


def bench_sync() -> float:
    """Benchmark: old serial sync scanner (via asyncio.run wrapper)."""
    orch = ProjectOrchestrator()
    t0 = time.perf_counter()
    report = orch.scan_directory(TARGET, no_llm=True)
    html = generate_html_observatory_report(report)
    elapsed = time.perf_counter() - t0
    print(f"[SYNC]  Serial:      {elapsed:.2f}s  ({report.total_files} files, {len(html):,} bytes HTML)")
    return elapsed


if __name__ == "__main__":
    print(f"\n[TARGET] {TARGET}\n{'=' * 50}")
    t_sync = bench_sync()
    t_async = asyncio.run(bench_async())
    speedup = t_sync / t_async if t_async > 0 else 1.0
    print(f"\n[SPEEDUP] {speedup:.1f}x faster with concurrent async scan")

