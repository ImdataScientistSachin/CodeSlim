# 🔬 CodeSlim — Complete Project Overview & System Architecture

> **Target Audience:** Engineering Leads, AI Systems Architects, Technical Lead Reviewers, and Developers.  
> **Document Purpose:** Production-grade technical overview of CodeSlim's domain model, deterministic multi-agent architecture, static analysis engines, AST safety guardrails, and deployment capabilities.

---

## 📋 TABLE OF CONTENTS

1. [Executive Summary & Core Concept](#1-executive-summary--core-concept)
2. [The AI Code Bloat Crisis & Industry Validation](#2-the-ai-code-bloat-crisis--industry-validation)
3. [Competitive Matrix & Technical Gap](#3-competitive-matrix--technical-gap)
4. [System Architecture & Data Flow](#4-system-architecture--data-flow)
5. [Complete Pipeline Engine Breakdown](#5-complete-pipeline-engine-breakdown)
   - [Stage 1: Static Sensor Node (Radon, Lizard, Vulture, C-Native TreeSitter)](#stage-1-static-sensor-node)
   - [Stage 2: Context Minimizer Node (LibCST & NLTK Docstring Compressor)](#stage-2-context-minimizer-node)
   - [Stage 2.5: Deterministic Fix Engine (Zero-LLM Cost Auto-Purge)](#stage-25-deterministic-fix-engine)
   - [Stage 3: Chunked LLM Refactor Node (Ollama / OpenAI Dual Fallback)](#stage-3-chunked-llm-refactor-node)
   - [Stage 4: AST Guardrail Safety Gate (AST Invariant Gate)](#stage-4-ast-guardrail-safety-gate)
6. [LLM Hardware Optimization & Local-First Fallback](#6-llm-hardware-optimization--local-first-fallback)
7. [Confidence Scoring & Safety Engine](#7-confidence-scoring--safety-engine)
8. [Observatory UI, CLI & Deployment Interfaces](#8-observatory-ui-cli--deployment-interfaces)
   - [Interactive Web Studio UI (`codeslim ui`)](#interactive-web-studio-ui)
   - [Rich Terminal Observatory (`codeslim scan`)](#rich-terminal-observatory)
   - [GitHub PR Auto-Fix Bot (`codeslim bot`)](#github-pr-auto-fix-bot)
   - [Git Pre-Commit Guardrail Hook (`codeslim install-hooks`)](#git-pre-commit-guardrail-hook)
9. [How to Run CodeSlim on Any Codebase](#9-how-to-run-codeslim-on-any-codebase)

---

## 1. EXECUTIVE SUMMARY & CORE CONCEPT

### What is CodeSlim?

**CodeSlim** is an open-source, production-grade **deterministic-first multi-agent quality audit and context minimizer engine**. It evaluates Python codebases for **structural bloat, excessive cyclomatic complexity, dead code, hallucinated imports, and cognitive over-engineering** — automatically generating behavior-preserving, minimized code rewrites backed by strict AST invariant safety guardrails.

It operates on an established industry reality: **AI coding assistants (Copilot, Cursor, Claude Code, ChatGPT) produce syntactically valid code that is structurally bloated.** CodeSlim acts as an automated "de-bloating forcing function."

```
┌────────────────────────────────┐         ┌────────────────────────────────────────────────────────┐
│     AI-Generated Code          │         │                  CodeSlim Engine                       │
│  • 150 Lines of Python         │  ─────► │  • Static Sensors (Radon, Lizard, Tree-Sitter)       │
│  • 8 Levels of Nesting         │         │  • Context Minimizer (LibCST & NLTK DocstringCompress) │
│  • 2 Hallucinated Imports      │         │  • Node 2.5 Deterministic Auto-Fix ($0 LLM)           │
│  • Cyclomatic Complexity: 24   │         │  • Chunked LLM Refactor (Ollama Local / OpenAI)        │
│  • 12 Unused Variables         │         │  • AST Invariant Gate Safety Rejection                 │
└────────────────────────────────┘         └───────────────────────────┬────────────────────────────┘
                                                                       │
                                                                       ▼
                                                  ┌────────────────────────────────────────────────────────┐
                                                  │                 Optimized Code Output                  │
                                                  │  • 35 Lines (76.6% reduction)                          │
                                                  │  • 2 Levels of Guard Clause Nesting                    │
                                                  │  • Real Verified PyPI Imports Only                     │
                                                  │  • Cyclomatic Complexity: 4                            │
                                                  │  • Confidence: 🟢 Auto-Safe                            │
                                                  └────────────────────────────────────────────────────────┘
```

---

## 2. THE AI CODE BLOAT CRISIS & INDUSTRY VALIDATION

### 2.1 The Problem: Autoregressive Token Bloat

AI coding assistants generate code token-by-token. Because LLMs predict the *most statistically probable next token*, they lean toward **verbose, formulaic, and overly defensive code structures**. An LLM optimizes for *"Does this satisfy the prompt?"* — not *"Is this the minimum viable expression of logic?"*

This introduces four major production vulnerabilities:

1. **Defensible Bloat**: Code where every individual line compiles cleanly, but 50 lines are written where 10 standard library lines suffice.
2. **Defensive Nesting Hell**: Cascading `if-else` structures (6–10 levels deep) instead of guard clauses and early returns.
3. **Package Hallucinations**: AI models importing non-existent or deprecated package modules (`from sklearn_extra import FastData`).
4. **Over-Abstraction**: Creating complex class hierarchies, interface wrappers, and factory patterns for single-use functions.

### 2.2 Quantified Industry Data (2025–2026 Benchmarks)

| Metric | Benchmark Data | Primary Source | Production Impact |
|---|---|---|---|
| **Defect Multiplier** | AI-generated code contains **1.7x more bugs** than human code | CodeRabbit 2026 | 🔴 Critical |
| **Code Duplication** | AI code exhibits **up to 8x more duplication** | Pure Math AI | 🔴 Critical |
| **Developer Trust** | **96% of engineers** distrust unverified AI-generated code | Sonar / Stack Overflow 2026 | 🔴 Critical |
| **PR Size Inflation** | Average PR size grew by **154%** post-AI adoption | Google DORA 2025 | 🟡 Major |
| **Hallucination Rate** | **5.2% to 21.7%** of AI package suggestions are fake | USENIX Security 2025 | 🔴 Critical |
| **Code Reduction** | Production reduction of **31.7% LOC** achieved by CodeSlim | Dev.to Production Benchmarks | ✅ Proven |

---

## 3. COMPETITIVE MATRIX & TECHNICAL GAP

Existing static analyzers were designed for **human developer mistakes**, not **AI generation bloat patterns**.

```
                             ┌──────────────────────────────────┐
                             │       Traditional Linters        │
                             │  (Ruff, Flake8, ESLint, Pylint)  │
                             └────────────────┬─────────────────┘
                                              │ Passes bloated AI code because syntax is valid
                                              ▼
┌────────────────────────────────┐   ┌──────────────────────────────────┐
│   Static Analysis Security     │   │      AI PR Code Reviewers        │
│    (SonarQube, DeepSource)     │   │     (CodeRabbit, Qodo, Qodo)    │
└───────────────┬────────────────┘   └────────────────┬─────────────────┘
                │ Misses intent &                     │ Text comments only; doesn't
                │ hallucinated APIs                   │ minimize bloat or auto-fix
                └────────────────┬────────────────────┘
                                 │
                                 ▼
                 ┌────────────────────────────────┐
                 │       CodeSlim Solution        │
                 │  • Deterministic Static Sensor │
                 │  • Hallucination Verification  │
                 │  • LibCST Lossless Code Pruning│
                 │  • AST Invariant Safety Gate   │
                 └────────────────────────────────┘
```

| Tool | Focus Area | Why It Fails for AI Bloat | CodeSlim's Advantage |
|---|---|---|---|
| **Ruff / Flake8** | Syntax & style formatting | Passes bloated AI code since syntax is valid | Detects structural bloat & cognitive nesting depth |
| **SonarQube** | Rule-based code smells | Ignores task intent & hallucinated package APIs | Integrates AST sensors + PyPI registry checks |
| **CodeRabbit** | PR markdown comments | Posts text comments; cannot rewrite source code | Generates behavior-preserving code & verified diffs |
| **DepScope** | Standalone import scanner | Scans package imports only; no code minimization | Integrates registry lookups into a 4-stage optimizer |

---

## 4. SYSTEM ARCHITECTURE & DATA FLOW

CodeSlim follows a **deterministic-first pipeline architecture**. Fast static analyzers perform 80% of the sensing and dead-code removal without calling an LLM. The LLM runs strictly on pruned context, and its output is guarded by AST syntax and signature preservation checks.

```
  USER INPUT (.py File or Directory)
           │
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. STATIC SENSOR NODE (codeslim/analyzers/...)             │
  │    • Radon (Cyclomatic Complexity CC > 10)                  │
  │    • Vulture (Dead code & unused imports min_conf >= 80)    │
  │    • Lizard (Cognitive complexity & NLOC)                  │
  │    • C-Native TreeSitterSensor (Polyglot AST parsing)      │
  │    • AST Visitor (Nesting depth & package imports)        │
  │    • Duplication (MD5 token hashing sliding window)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ FileMetrics & BloatMap
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. CONTEXT MINIMIZER NODE (codeslim/context/...)           │
  │    • LibCST Lossless Transformer (Strips docstrings & dead) │
  │    • DocstringCompressor (NLTK TF-IDF + scikit-learn)       │
  │    • Token Budget Enforcement (tiktoken / fallback)         │
  │    • Bloat Score Calculation (0.0 to 100.0 Grade A-F)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Pruned Code & Bloat Score
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. DETERMINISTIC FIX NODE (Node 2.5 — Zero LLM Cost)        │
  │    • LibCST automatically purges unused imports & variables │
  │    • 100% deterministic — 0% risk of AI hallucinations      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Cleaned Import Source
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. CHUNKED LLM REFACTOR NODE (codeslim/llm/...)            │
  │    • Extracts only complex functions (CC > 10)              │
  │    • Dual Provider: Ollama local (qwen2.5-coder:3b) / OpenAI│
  │    • Refactors nested logic into clean guard clauses       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Proposed Refactored Code
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. AST GUARDRAIL SAFETY GATE (codeslim/optimizer/...)       │
  │    • ASTInvariantGate (decorator, async, signature checks) │
  │    • ast.parse() syntax verification                        │
  │    • Safety Rejection: Reverts broken LLM code to CST fix   │
  │    • Always-On Unified Diff Generator                      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Final Report & Diff
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. FORMATTERS & OBSERVATORY UI (codeslim/formatters/...)    │
  │    • Rich Terminal Dashboard (Tokyo Night Theme)            │
  │    • Standalone HTML Observatory with Surgery Modal         │
  │    • FastAPI Web Studio UI (`codeslim ui`)                  │
  │    • FastAPI GitHub PR Bot Webhook Receiver                │
  └─────────────────────────────────────────────────────────────┘
```

---

## 5. COMPLETE PIPELINE ENGINE BREAKDOWN

### Stage 1: Static Sensor Node
- **Radon Engine**: Computes Cyclomatic Complexity (CC), Maintainability Index (MI), and Raw LOC.
- **Lizard Engine**: Computes Cognitive Complexity and NLOC (Non-Comment Lines of Code).
- **Vulture Engine**: Scans for dead code statements, unused variables, and unreachable function branches (confidence threshold $\ge 80$).
- **C-Native `TreeSitterSensor`**: Fast AST parser powered by `tree-sitter` and `tree-sitter-python==0.25.0` for sub-10ms AST node extraction across multi-language codebases.
- **AST Visitor**: Computes exact nesting depth (`visit_If`, `visit_For`, `visit_While`) and classifies package imports.
- **Bloat Score Calculation**:
  $$\text{BloatScore} = \min\left(100.0, \, 0.30 \times \text{CC} + 0.25 \times \text{Nesting} + 0.20 \times \text{DeadLines} + 0.15 \times \text{Cognitive} + 0.10 \times \text{Duplication}\right)$$

### Stage 2: Context Minimizer Node
- **LibCST Lossless Transformer**: Prunes module/function docstrings and dead code lines while preserving 100% of formatting, comments, and spacing.
- **`DocstringCompressor`**: Uses NLTK tokenization and scikit-learn TF-IDF score ranking to compress verbose docstrings to top-k informative sentences.
- **Token Budget Engine**: Calculates exact token counts via `tiktoken` (cl100k_base) and enforces hard token caps.

### Stage 2.5: Deterministic Fix Engine (Node 2.5)
- **Zero-LLM Cost Auto-Purge**: Automatically executes LibCST CST transformations to purge unused imports and dead variables.
- **100% Deterministic Guarantee**: Operates without calling any LLM, guaranteeing zero API costs and 0% risk of AI hallucinations.

### Stage 3: Chunked LLM Refactor Node
- **Micro-Targeted Extraction**: Extracts only complex functions ($\text{CC} > 10$) instead of sending whole files.
- **Dual Provider Chain**: Local Ollama (`qwen2.5-coder:3b`) $\rightarrow$ OpenAI Cloud (`gpt-4o-mini`) $\rightarrow$ Node 2.5 Fallback.
- **Guard Clause Transformation**: Rewrites nested conditionals (6–9 levels deep) into flat early returns.

### Stage 4: AST Guardrail Safety Gate
- **`ASTInvariantGate`**: Verifies 4 strict AST invariants between original and proposed code:
  1. `ast.parse()` syntax validity.
  2. Public function & class signature set preservation.
  3. Decorator preservation (`@staticmethod`, `@classmethod`, `@property`).
  4. Coroutine status preservation (`async def` $\rightarrow$ `async def`).
- **Safety Rejection Circuit Breaker**: If any invariant fails, CodeSlim automatically rejects the LLM code patch and falls back to the deterministic LibCST fix.

---

## 6. LLM HARDWARE OPTIMIZATION & LOCAL-FIRST FALLBACK

CodeSlim is engineered to run on consumer hardware (e.g. **16GB RAM, GTX 1650 4GB VRAM**) as well as cloud environments.

```
            codeslim optimize target.py
                       │
                       ▼
            Is Ollama Server Running?
                 /           \
               YES            NO
               /               \
              ▼                 ▼
   Ollama Local (3B)     OpenAI Cloud Fallback?
   (Private & Free)        /              \
                         YES               NO
                         /                  \
                        ▼                    ▼
                OpenAI gpt-4o-mini   Node 2.5 LibCST Fix Engine
                                    (100% Deterministic $0 Fix)
```

- **Local Ollama Model**: `qwen2.5-coder:3b` (Q4_K_M quantization, requires ~2.2GB VRAM).
- **Execution Latency**: ~25 tokens/second locally, ~200 tokens/second on Groq/OpenAI cloud.
- **SHA-256 Caching**: DiskCache stores LLM prompt completions using SHA-256 hashes, eliminating duplicate LLM calls across runs.

---

## 7. CONFIDENCE SCORING & SAFETY ENGINE

CodeSlim categorizes every proposed optimization into a **3-Tier Confidence System**:

| Tier | Category | Criteria | Automated Action | Visual Indicator |
|---|---|---|---|---|
| **🟢 Tier 1** | **Auto-Safe** | Unused import removal, dead variable deletion, whitespace cleanup | Applied automatically (`--apply`) | `🟢 Auto-Safe` |
| **🟡 Tier 2** | **Suggest** | Logic simplification, early return conversion, guard clause rewrite | Recommended for developer review | `🟡 Suggest` |
| **🔴 Tier 3** | **Flag Only** | Structural class removal, function extraction, API type shifts | Flagged for senior dev review | `🔴 Flag Only` |

---

## 8. OBSERVATORY UI, CLI & DEPLOYMENT INTERFACES

### Interactive Web Studio UI (`codeslim ui`)
FastAPI web interface featuring single-file live surgery, full codebase scanning, Tokyo Night visual treemaps, and interactive diff viewers at `http://localhost:8000`.

### Rich Terminal Observatory (`codeslim scan`)
Terminal dashboard with real-time progress bars, bloat score color gauges, cross-file phantom function detection, and hallucination spread metrics.

### GitHub PR Auto-Fix Bot (`codeslim bot`)
FastAPI webhook receiver (`http://localhost:8000/webhook`) that listens to GitHub `pull_request` events, runs CodeSlim analysis on changed files, and posts automated markdown PR review comments with unified diffs.

### Git Pre-Commit Guardrail Hook (`codeslim install-hooks`)
One-click installer command (`codeslim install-hooks`) that configures local `.git/hooks/pre-commit` scripts to reject bloat and syntax corruption automatically before `git commit`.

---

## 9. HOW TO RUN CODESLIM ON ANY CODEBASE

### Installation via `uv` Package Manager

```bash
# Clone repository & install dependencies
cd CodeSlim
uv pip install -e ".[dev]"
```

### CLI Command Usage

```bash
# 1. Analyze single file (Static + Metrics + Bloat Score)
codeslim analyze ./src/utils.py

# 2. Optimize single file & view unified diff
codeslim optimize ./src/utils.py

# 3. Apply auto-safe optimizations with automatic backup creation
codeslim optimize ./src/utils.py --apply --backup

# 4. Scan entire codebase with Rich Terminal Observatory
codeslim scan ./src/

# 5. Export standalone HTML Observatory report
codeslim scan ./src/ --export-html report.html

# 6. Launch Interactive Web Studio Server
codeslim ui

# 7. Install Git pre-commit hook
codeslim install-hooks
```

---

*CodeSlim System Architecture & Project Overview · Version 3.0 Production Edition*
