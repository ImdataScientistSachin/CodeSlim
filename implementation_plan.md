# 🚀 CodeSlim 2.0: Implementation Plan & Architecture Roadmap

> **Target Version**: CodeSlim v2.0 (The Deterministic AI Output Governance Gateway)  
> **Core Identity**: Sitting as a model-agnostic, deterministic security and quality gateway between autonomous AI agents / developers and git repositories.

---

## 🎯 Executive Summary & Strategic Objectives

CodeSlim 2.0 evolves from a single-file CLI/Web Studio minimizer into a **Deterministic AI Output Governance Gateway & System-Level Code Intelligence Engine**.

### Primary Objectives for v2.0:
1. **Zero Hallucinated Dependency Incidents**: Active PyPI JSON API & DepScope verification blocking un-verified packages before CI build execution.
2. **Dynamic Confidence Degradation**: Automatic fallbacks based on test coverage (Coverage < 30% degrades strictly to Node 2.5 Deterministic LibCST Mode).
3. **Tier 2 Differential Test Execution Gate**: Automated `pytest` execution running baseline vs post-refactor suites to guarantee 0 behavioral regressions.
4. **System-Level Architectural Graph Intelligence**: Evolving cross-file analysis to detect circular dependency sprawl, layer boundary violations, and cross-module phantom symbols.
5. **40% AI Token Cost Reduction Telemetry**: Built-in dollar-denominated token spend reduction tracker.

---

## 🏗️ Architectural Milestone Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CODESLIM v2.0 MILESTONE ROADMAP                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ MILESTONE 1: TELEMETRY ENGINE & CORE 4 HARDENING                            │
│ • Telemetry Tracker (Token $ saved, AST rejections, Hallucination blocks)  │
│ • Async PyPI Batch Lookup & Registry Cache                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ MILESTONE 2: DYNAMIC CONFIDENCE DEGRADATION & TEST GATE                     │
│ • Coverage-based Degradation Engine                                         │
│ • Differential pytest Execution Runner & Auto-Rollback Gate                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ MILESTONE 3: SYSTEM-LEVEL DEPENDENCY GRAPH ENGINE                           │
│ • Cross-Module Layer Violation & Circular Import Detector                   │
│ • Project-Wide Phantom Symbol Graph                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ MILESTONE 4: ENTERPRISE CI GOVERNANCE & GITHUB BOT                          │
│ • Node 2.5 Auto-Apply vs Node 3 PR-Only Policy Enforcer                     │
│ • Zero-Permission Web Studio Playground & HTML Observatory Export           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Phase & Component Specifications

### Component 1: Telemetry & Financial Savings Engine
* **Goal**: Track empirical financial and security value delivered per file scan and PR execution.
* **New File**: `codeslim/telemetry/tracker.py`
* **Features**:
  * `tokens_saved_count`: Exact integer of prompt tokens pruned.
  * `dollars_saved_usd`: Calculated based on target model pricing (GPT-4o, Claude 3.5 Sonnet).
  * `hallucinated_packages_blocked`: Count of non-existent PyPI package calls intercepted.
  * `ast_gate_rejections`: Count of invalid AST mutations caught.

### Component 2: Dynamic Confidence Degradation & Differential Test Gate
* **Goal**: Guarantee zero behavioral regressions when test suites are weak, absent, or present.
* **New File**: `codeslim/optimizer/test_gate.py`
* **New File**: `codeslim/pipeline/confidence_degradation.py`
* **Workflow**:
  ```
  Test Coverage Assessment ──► Coverage < 30% ──► Node 2.5 Deterministic Mode (0% LLM Risk)
                           ──► Coverage 30-80%──► PR Suggestion-Only Mode (Human Review)
                           ──► Coverage > 80% ──► Differential Pytest Gate (Auto-Write if Pass)
  ```

### Component 3: System-Level Architectural Graph Analyzer
* **Goal**: Move from file-level micro metrics ($CC$, nesting) to repository-wide dependency integrity.
* **New File**: `codeslim/analyzers/system_graph.py`
* **Features**:
  * Multi-module symbol dependency matrix.
  * Circular import detection (`import A -> B -> A`).
  * Architectural layer boundary enforcement (e.g. `domain` modules cannot import `ui` or `infrastructure`).

### Component 4: Policy-Driven Enterprise CI Governance Bot
* **Goal**: Enforce strict CI write policies on incoming AI agent Pull Requests.
* **File to Update**: [pr_handler.py](file:///g:/Project%20Directory/AGENTIC%20AI%20PROJECT%20DIRECTORY/CodeSlim/codeslim/bot/pr_handler.py)
* **Policy Matrix**:
  * `Node 2.5 (LibCST Deterministic Fixes)` $\rightarrow$ **Auto-Apply Allowed** (Loss-less syntax changes).
  * `Node 3 (LLM Generative Refactoring)` $\rightarrow$ **PR-Only / Suggestion Diff** (Requires human review click).

---

## 🧪 Verification Plan

### Automated Test Suite
- `tests/telemetry/test_tracker.py`: Test dollar cost calculation and token metrics aggregation.
- `tests/optimizer/test_differential_gate.py`: Test `pytest` sub-process execution and automatic rollback on test failure.
- `tests/analyzers/test_system_graph.py`: Test circular import detection and cross-module phantom symbol extraction.
- `tests/pipeline/test_confidence_degradation.py`: Test automatic fallback to Node 2.5 when coverage < 30%.

### Manual & Real-World Benchmark Verification
- Execute `codeslim scan ./codeslim --export-html docs/index.html` and verify live telemetry metrics display in the Observatory dashboard.
- Run a 100-file project scan in `--no-llm` mode to benchmark < 2s execution velocity.

---

## 🏁 Definition of Done (DoD) for CodeSlim 2.0
1. All 4 components implemented with 100% strict type hints and Google-style docstrings.
2. 0 errors on `python -m ruff check codeslim/ tests/`.
3. 0 errors on `python -m mypy codeslim/`.
4. 100% green passing result on full test suite (`python -m pytest -v`).
5. Updated documentation in [CODESLIM_GUIDE.md](file:///g:/Project%20Directory/AGENTIC%20AI%20PROJECT%20DIRECTORY/CodeSlim/documents/CODESLIM_GUIDE.md).
