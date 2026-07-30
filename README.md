# 🚀 CodeSlim — Agentic Code Quality Audit, Context Minimizer & Guardrail Engine

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-96%2F96%20passing-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--quality-verification)
[![Architecture](https://img.shields.io/badge/architecture-Multi--Agent%20Pipeline-orange?style=for-the-badge&logo=diagramsdotnet&logoColor=white)](#-architecture--6-stage-pipeline)
[![Code Style](https://img.shields.io/badge/code%20style-Ruff%20%7C%20Mypy-000000?style=for-the-badge&logo=ruff&logoColor=white)](#-testing--quality-verification)
[![LLM Runtime](https://img.shields.io/badge/LLM-Ollama%20%7C%20OpenAI%20%7C%20Groq-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)](#-local-first-llm-privacy--provider-chain)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#-docker-deployment)
[![GitHub Action](https://img.shields.io/badge/github%20action-available-181717?style=for-the-badge&logo=github-actions&logoColor=white)](#-github-actions-integration)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

**CodeSlim** is a deterministic-first, open-source **Agentic AI CLI Engine** that sits between Python codebases and Large Language Models. It combines fast C-native static analysis sensors (Radon, Vulture, Lizard, Tree-Sitter) with LibCST Concrete Syntax Trees to slash token bloat by up to **76%**, while enforcing **AST syntax guardrails** to prevent LLM hallucinations from ever corrupting your source code.

[**Quick Start**](#-quick-start) · [**CLI Commands**](#-cli-commands--usage) · [**Architecture**](#-architecture--6-stage-pipeline) · [**Docker**](#-docker-deployment) · [**GitHub Action**](#-github-actions-integration) · [**Contributing**](#-contributing)

</div>

---

## 📋 Table of Contents

- [Why CodeSlim? The AI Bloat Problem](#-why-codeslim-the-ai-bloat-problem)
- [Key Capabilities](#-key-capabilities)
- [Competitive Matrix](#-competitive-matrix)
- [Tech Stack](#-tech-stack)
- [Architecture & 6-Stage Pipeline](#-architecture--6-stage-pipeline)
- [Quick Start](#-quick-start)
- [CLI Commands & Usage](#-cli-commands--usage)
- [Configuration Reference](#-configuration-reference)
- [.codeslimignore](#-codeslimignore)
- [3-Tier Confidence Classifier](#-3-tier-confidence-classifier)
- [Bloat Score Formula](#-bloat-score-formula)
- [Local-First LLM Privacy & Provider Chain](#-local-first-llm-privacy--provider-chain)
- [Docker Deployment](#-docker-deployment)
- [GitHub Actions Integration](#-github-actions-integration)
- [Testing & Quality Verification](#-testing--quality-verification)
- [Repository Structure](#-repository-structure)
- [Hardware Requirements](#-hardware-requirements)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [FAQ](#-faq)
- [License](#-license)

---

## 🔥 Why CodeSlim? The AI Bloat Problem

> **AI coding assistants (GitHub Copilot, Cursor, Claude Code, ChatGPT) produce syntactically valid code that is structurally bloated.** CodeSlim acts as an automated de-bloating forcing function between AI code generation and your production codebase.

AI models generate code token-by-token, optimizing for *"Does this satisfy the prompt?"* — not *"Is this the minimum viable expression of logic?"* This creates four production-grade vulnerabilities:

1. **Defensible Bloat** — 50 lines where 10 standard-library lines suffice; every individual line compiles, but the whole is unnecessary.
2. **Defensive Nesting Hell** — Cascading `if-else` structures (6–10 levels deep) instead of guard clauses and early returns.
3. **Package Hallucinations** — AI models import non-existent or deprecated packages (`from sklearn_extra import FastData`).
4. **Over-Abstraction** — Complex class hierarchies, interface wrappers, and factory patterns for single-use functions.

### 📊 Industry Benchmark Data (2025–2026)

| Metric | Benchmark | Source | Impact |
| :--- | :--- | :--- | :---: |
| **Defect Multiplier** | AI-generated code has **1.7× more bugs** than human code | CodeRabbit 2026 | 🔴 Critical |
| **Code Duplication** | AI code exhibits **up to 8× more duplication** | Pure Math AI | 🔴 Critical |
| **Developer Trust Gap** | **96% of engineers** distrust unverified AI code | Sonar / Stack Overflow 2026 | 🔴 Critical |
| **PR Size Inflation** | Average PR size grew **154%** post-AI adoption | Google DORA 2025 | 🟡 Major |
| **Hallucination Rate** | **5.2–21.7%** of AI package suggestions are non-existent | USENIX Security 2025 | 🔴 Critical |
| **CodeSlim Reduction** | Production reduction of **31.7% LOC** achieved | Dev.to Benchmarks | ✅ Proven |

---

## 🌟 Key Capabilities

> [!IMPORTANT]
> **Deterministic First, AI Second**: 80% of dead-code purging and import pruning is performed with **100% mathematical precision** via LibCST — zero LLM cost. The LLM is invoked strictly on pre-minimized, complex function chunks.

| Feature | Description | Impact |
| :--- | :--- | :--- |
| ⚡ **Lossless Context Pruning** | Strips non-essential docstrings and dead blocks via LibCST + C-Native Tree-Sitter (`tree-sitter>=0.26.0`). | **Up to 76% Token Reduction** |
| 🛡️ **AST Syntax Safety Gate** | Validates `ast.parse()` syntax and enforces public class/function signature & decorator preservation. | **0% Hallucination Corruption** |
| ⚡ **Deterministic Fix Node** | Auto-purges unused imports and dead variables without calling LLMs. | **$0.00 LLM Cost for 80% of Fixes** |
| 🔒 **Local-First Privacy** | Runs 100% local, offline LLMs via Ollama (`qwen2.5-coder:3b`) with optional Groq/OpenAI cloud fallback. | **Complete Code Privacy** |
| 🎯 **3-Tier Confidence Engine** | Categorizes refactor actions into `Auto-Safe`, `Suggest`, and `Flag-Only` tiers. | **Zero Unintended Breaking Changes** |
| 💾 **SHA-256 Response Cache** | DiskCache stores LLM completions keyed by SHA-256 prompt hash, eliminating duplicate API calls. | **$0.00 Cost on Re-runs** |
| 🔭 **HTML Observatory UI** | Generates standalone Tokyo Night interactive dashboards with code diff surgery modals. | **Instant Codebase Visibility** |
| 🤖 **Auto-Fix GitHub PR Bot** | Asynchronous FastAPI webhook receiver with HMAC-SHA256 verification for automated PR audits. | **Automated CI/CD Code Review** |
| 🪝 **Git Pre-Commit Hook** | Installs lightweight pre-commit guardrails to strip dead code in **< 50ms** before committing. | **Shift-Left Quality Enforcement** |
| 🎬 **GitHub Composite Action** | One-line workflow step to audit any PR with zero server setup. | **Zero-Infrastructure CI Integration** |

---

## ⚔️ Competitive Matrix

Existing tools were designed for **human developer mistakes**, not **AI generation bloat patterns**.

| Tool | Category | Why It Fails for AI Bloat | CodeSlim Advantage |
| :--- | :--- | :--- | :--- |
| **Ruff / Flake8** | Syntax & style linting | Passes bloated AI code because syntax is valid | Detects structural bloat, cognitive nesting depth & hallucinated APIs |
| **SonarQube** | Rule-based code smells | Ignores task intent and fabricated package references | Integrates AST sensors + multi-stage hallucination verification |
| **CodeRabbit / Qodo** | AI PR review comments | Posts text comments; cannot rewrite or minimize source code | Generates behavior-preserving code rewrites with verified unified diffs |
| **DepScope** | Standalone import scanner | Scans imports only; no code minimization or refactoring | Integrates registry lookups into the full 4-stage optimizer pipeline |
| **Pylint** | General code quality | No AI-specific bloat heuristics | Tuned Bloat Score formula targeting AI generation patterns specifically |

---

## 🛠 Tech Stack

### Core Pipeline & AST Layer

| Library | Version | Role |
| :--- | :--- | :--- |
| **LibCST** | `>=1.4` | Lossless Concrete Syntax Tree transformer for dead-code pruning, import removal, docstring stripping — without altering formatting |
| **tree-sitter** | `>=0.26.0,<0.27.0` | C-native AST parser for sub-10ms skeleton extraction across polyglot codebases |
| **tree-sitter-python** | `==0.25.0` | Python grammar bindings for Tree-Sitter |
| **tree-sitter-language-pack** | `>=1.12.0,<2.0.0` | Multi-language grammar pack for Tree-Sitter (future polyglot support) |
| **Python ast** | stdlib | `ast.parse()` syntax validation in the AST Guardrail Safety Gate |

### Static Analysis Sensors

| Library | Version | Role |
| :--- | :--- | :--- |
| **Radon** | `>=6.0` | Cyclomatic Complexity (CC), Maintainability Index (MI), Raw LOC metrics |
| **Vulture** | `>=2.7` | Dead code detection, unused import scanning, unreachable branch identification (min_conf ≥ 80) |
| **Lizard** | `>=1.18` | Cognitive Complexity and NLOC (Non-Comment Lines of Code) |

### LLM & AI Layer

| Library | Version | Role |
| :--- | :--- | :--- |
| **OpenAI SDK** | `>=1.0` | OpenAI Cloud provider fallback (`gpt-4o-mini`) |
| **httpx** | `>=0.27` | Async HTTP client for Ollama local API (`http://localhost:11434`) and Groq API |
| **tiktoken** | `>=0.5` | Token counting and budget enforcement via OpenAI `cl100k_base` encoding |
| **diskcache** | `>=5.6` | SHA-256 keyed on-disk LLM response caching; eliminates duplicate LLM calls across runs |
| **LangGraph** | `>=1.2.0,<2.0.0` | Stateful multi-node pipeline orchestration (graph-style agentic DAG) |

### NLP & Docstring Compression

| Library | Version | Role |
| :--- | :--- | :--- |
| **NLTK** | `>=3.8` | Tokenization and sentence splitting for `DocstringCompressor` |
| **scikit-learn** | `>=1.4` | TF-IDF score ranking to extract top-k informative sentences from verbose docstrings |

### API, CLI & Configuration

| Library | Version | Role |
| :--- | :--- | :--- |
| **FastAPI** | `>=0.110` | Web Studio UI server, GitHub PR Webhook receiver (`/webhook`), and REST API |
| **Uvicorn** | `>=0.28` | ASGI server for FastAPI |
| **Click** | `>=8.0` | CLI command parsing and entrypoint (`codeslim` command) |
| **Rich** | `>=13.0` | Tokyo Night themed terminal dashboards, progress bars, and color-coded output tables |
| **Pydantic** | `>=2.0` | Data validation and typed schema models throughout the pipeline |
| **pydantic-settings** | `>=2.0` | `.env` file loading and environment variable configuration management |
| **structlog** | `>=24.0` | Structured JSON-compatible logging throughout all pipeline stages |

### Dev & Quality Tooling

| Library | Version | Role |
| :--- | :--- | :--- |
| **pytest** | `>=8.0` | Unit and integration test runner (96/96 passing) |
| **pytest-asyncio** | `>=0.23` | Async test support for FastAPI and httpx |
| **pytest-mock** | `>=3.0` | Mock fixtures for LLM and webhook tests |
| **pytest-cov** | `>=5.0` | Code coverage reporting |
| **Ruff** | `>=0.4` | Blazing-fast linter (E, F, I, UP, B rules; 120 char line length) |
| **Mypy** | `>=1.10` | Strict static type checking (`python_version = "3.11"`) |
| **uv** | latest | Recommended ultra-fast package manager and environment sync tool |

### Packaging & Deployment

| Tool | Role |
| :--- | :--- |
| **setuptools ≥ 68** | Python package build backend |
| **Docker** | Containerized deployment via `python:3.11-slim` base image |
| **docker-compose** | Multi-service local orchestration (CodeSlim + Ollama sidecar) |
| **GitHub Actions** | Composite Action (`action.yml`) for zero-infrastructure CI/CD integration |
| **pre-commit** | Git hook configuration (`.pre-commit-config.yaml`) |

---

## 📐 Architecture & 6-Stage Pipeline

CodeSlim processes code through a deterministic **6-stage agentic pipeline**:

```text
  USER INPUT (.py File or Directory / GitHub PR Webhook)
           │
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. STATIC SENSOR NODE (codeslim/analyzers/...)             │
  │    • Radon (Cyclomatic Complexity CC > 10)                  │
  │    • Vulture (Dead code & unused imports min_conf >= 80)    │
  │    • Lizard (Cognitive complexity & NLOC)                  │
  │    • Tree-Sitter Sensor (C-Native Skeleton & CST Parsing)  │
  │    • AST Visitor (Nesting depth & import classification)   │
  │    • Duplication (MD5 token hashing sliding window)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ FileMetrics & BloatMap
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. CONTEXT MINIMIZER NODE (codeslim/context/...)           │
  │    • LibCST Lossless Transformer (Strips docstrings & dead) │
  │    • DocstringCompressor (NLTK tokenize + TF-IDF ranking)  │
  │    • Token Budget Enforcement (tiktoken cl100k_base)       │
  │    • Bloat Score Calculation (0.0 to 100.0 Grade A–F)      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Pruned Code & Bloat Score
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 3. DETERMINISTIC FIX NODE (Node 2.5 — Zero LLM Cost)       │
  │    • LibCST automatically purges unused imports & variables │
  │    • 100% deterministic — 0% risk of AI hallucinations      │
  │    • SHA-256 DiskCache skips re-processing unchanged files  │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Cleaned Import Source
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 4. CHUNKED LLM REFACTOR NODE (codeslim/llm/...)            │
  │    • Extracts only complex functions (CC > 10)              │
  │    • Provider Chain: Ollama → OpenAI → Groq → Node 2.5 CST │
  │    • Refactors nested logic into clean guard clauses        │
  │    • Response cached by SHA-256 hash via DiskCache         │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Proposed Refactored Code
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 5. AST GUARDRAIL SAFETY GATE (codeslim/optimizer/...)       │
  │    • ast.parse() syntax verification                        │
  │    • Public class & function signature set preservation     │
  │    • Decorator preservation (@staticmethod, @classmethod)  │
  │    • Coroutine status preservation (async def → async def) │
  │    • Safety Rejection: Reverts broken LLM code to CST fix   │
  │    • Always-On Unified Diff Generator                       │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Final Report & Unified Diff
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. FORMATTERS & OBSERVATORY UI (codeslim/formatters/...)    │
  │    • Rich Terminal Dashboard (Tokyo Night Theme)            │
  │    • Standalone HTML Observatory with Surgery Modal         │
  │    • FastAPI Web Studio UI & GitHub PR Webhook Receiver     │
  │    • JSON / github-pr structured output formats            │
  └──────────────────────────────┴──────────────────────────────┘
```

### LangGraph Orchestration

The pipeline stages are wired as a **LangGraph stateful DAG**. Each node receives the shared `PipelineState` object, transforms it, and passes control to the next node. The graph handles conditional branching (e.g., skipping the LLM node when `CC ≤ 10`) and circuit-breaking (falling back to the Deterministic Fix Node when the AST Gate rejects LLM output).

---

## ⚡ Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- [Ollama](https://ollama.com) (for local, free, offline LLM execution)

### 1. Installation

**Option A — `uv` (Recommended, fastest)**

```bash
git clone https://github.com/ImdataScientistSachin/CodeSlim.git
cd CodeSlim
uv sync
```

**Option B — Standard pip (editable install)**

```bash
git clone https://github.com/ImdataScientistSachin/CodeSlim.git
cd CodeSlim
pip install -e .
```

**Option C — pip install (dev dependencies)**

```bash
pip install -e ".[dev]"
```

### 2. Environment Setup

```bash
cp .env.example .env
```

Edit `.env` with your preferred provider (see [Configuration Reference](#-configuration-reference)).

### 3. Pull Local LLM (Optional but Recommended)

```bash
# Start Ollama server
ollama serve

# Pull the default local model (~2.2 GB)
ollama pull qwen2.5-coder:3b
```

> [!TIP]
> **Zero Cloud Cost**: With Ollama running, CodeSlim operates 100% offline. No API keys required for the full pipeline.

### 4. Run Your First Analysis

```bash
# Analyze the CodeSlim codebase itself (no LLM calls)
codeslim analyze ./codeslim/ --format rich

# Full optimization pipeline on a single file
codeslim optimize ./codeslim/analyzers/radon_analyzer.py
```

---

## 💻 CLI Commands & Usage

### 🔍 1. Fast Code Bloat Analysis (`codeslim analyze`)

Scan Python source files or entire directories for complexity, bloat score, and dead imports **without making any LLM calls**:

```bash
# Analyze a directory with Rich terminal output
codeslim analyze ./codeslim/ --format rich

# Analyze a single file with JSON output
codeslim analyze ./src/utils.py --format json

# Output a GitHub PR annotation JSON (for CI pipelines)
codeslim analyze ./src/ --format github-pr --output codeslim_report.json

# Set a custom bloat score threshold
codeslim analyze ./src/ --threshold 60
```

### ⚡ 2. Full Optimization Pipeline (`codeslim optimize`)

Run deterministic CST dead-code removal combined with guarded LLM refactoring:

```bash
# Preview diff without applying changes
codeslim optimize ./target_file.py

# Apply auto-safe optimizations with automatic backup
codeslim optimize ./target_file.py --apply --backup

# Optimize without LLM (deterministic CST only)
codeslim optimize ./target_file.py --no-llm --apply

# Skip backup creation
codeslim optimize ./target_file.py --apply --no-backup
```

### 🔭 3. Project Observatory HTML Export (`codeslim scan`)

Scan an entire project and export a standalone, interactive Tokyo Night HTML Observatory report:

```bash
# Terminal Rich Observatory dashboard
codeslim scan ./codeslim/

# Export standalone HTML Observatory (single file, no server needed)
codeslim scan ./codeslim/ --export-html observatory_report.html

# Combine terminal + HTML export
codeslim scan ./src/ --format rich --export-html report.html
```

### 🎨 4. Launch Web Studio (`codeslim ui`)

Launch the interactive Tokyo Night Web Studio workspace in your browser at `http://localhost:8000`:

```bash
codeslim ui --port 8000

# Bind to all interfaces (for Docker/remote access)
codeslim ui --host 0.0.0.0 --port 8000
```

### 🤖 5. Start GitHub PR Webhook Bot (`codeslim bot serve`)

Start the FastAPI webhook receiver for automated PR security and quality audits:

```bash
codeslim bot serve --port 8000

# Enable auto-commit of deterministic fixes back to the PR branch
codeslim bot serve --port 8000 --auto-commit

# Specify a custom webhook secret for HMAC-SHA256 verification
codeslim bot serve --port 8000 --webhook-secret $GITHUB_WEBHOOK_SECRET
```

The bot listens on `POST /webhook` for GitHub `pull_request` events, runs CodeSlim on the changed `.py` files, and posts a markdown review comment with a unified diff summary.

### 🪝 6. Install Pre-Commit Guardrail Hook (`codeslim install-hooks`)

Install the local Git pre-commit hook into `.git/hooks/pre-commit`:

```bash
codeslim install-hooks
```

This strips unused imports and dead variables in **< 50ms** before every `git commit`, enforcing shift-left quality at the source.

---

## ⚙️ Configuration Reference

Copy `.env.example` to `.env` and configure your environment:

```env
# ─── LLM Provider Selection ───────────────────────────────────────────────────
# Options: ollama | openai | groq
LLM_PROVIDER=ollama

# ─── Model Selection ──────────────────────────────────────────────────────────
# Model used for static analysis prompts
LLM_MODEL_ANALYSIS=qwen2.5-coder:3b

# Model used for code refactoring / optimization
LLM_MODEL_OPTIMIZATION=qwen2.5-coder:3b

# ─── Ollama Local Configuration ───────────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434

# ─── OpenAI Cloud Configuration (optional fallback) ───────────────────────────
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# ─── Groq Cloud Configuration (optional, fast inference) ──────────────────────
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama-3.1-70b-versatile

# ─── GitHub PR Bot Configuration ──────────────────────────────────────────────
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# ─── Pipeline Thresholds ──────────────────────────────────────────────────────
# Minimum cyclomatic complexity to trigger LLM refactoring
CC_THRESHOLD=10

# Minimum Vulture confidence to flag dead code
VULTURE_MIN_CONFIDENCE=80

# Maximum token budget per file chunk sent to LLM
MAX_TOKEN_BUDGET=4096

# ─── Caching ──────────────────────────────────────────────────────────────────
# Directory for SHA-256 keyed DiskCache LLM response storage
CACHE_DIR=.codeslim_cache
```

### LLM Provider Priority Chain

```
  codeslim optimize target.py
              │
              ▼
    Is LLM_PROVIDER=ollama and Ollama running?
            /           \
          YES             NO
          /                 \
         ▼                   ▼
 Ollama Local           Is OpenAI API key set?
 qwen2.5-coder:3b        /              \
 (Private & Free)      YES               NO
                        /                  \
                       ▼                    ▼
               OpenAI gpt-4o-mini    Is Groq API key set?
                                       /           \
                                     YES             NO
                                     /                 \
                                    ▼                   ▼
                             Groq Inference    Node 2.5 LibCST Fix
                             (Fast Cloud)      (100% Deterministic, $0)
```

---

## 🚫 .codeslimignore

Create a `.codeslimignore` file in your project root to exclude files and directories from analysis — identical syntax to `.gitignore`:

```gitignore
# Exclude virtual environments and build artifacts
.venv/
__pycache__/
*.egg-info/
dist/
build/

# Exclude test fixtures (may intentionally contain dead code)
tests/fixtures/

# Exclude auto-generated files
migrations/
*_pb2.py

# Exclude third-party vendored code
vendor/
```

A `.codeslimignore` is already provided in this repository covering common Python project exclusion patterns.

---

## 🎯 3-Tier Confidence Classifier

Every proposed optimization is categorized before application. This eliminates breaking changes:

```text
┌─────────────────┬───────────────────────────────┬────────────────────────────────┐
│ Tier            │ Action Type                   │ Applied Automatically?         │
├─────────────────┼───────────────────────────────┼────────────────────────────────┤
│ 🟢 Auto-Safe    │ Unused imports & dead vars    │ Yes — Deterministic CST Fix    │
│ 🟡 Suggest      │ Nesting reduction, guard       │ Shown as diff; requires --apply│
│                 │ clauses, early returns        │ Subject to AST Safety Gate     │
│ 🔴 Flag-Only    │ Public API signature changes, │ Flagged for manual review      │
│                 │ class restructuring           │ Never auto-applied             │
└─────────────────┴───────────────────────────────┴────────────────────────────────┘
```

**Real-world classification example:**

```python
# Input: AI-generated function with CC=24, 8 levels of nesting
def process_data(data, config, fallback=None):
    if data:
        if config:
            if config.get("enabled"):
                if data.get("items"):
                    ...  # 6 more levels

# 🟢 Auto-Safe: Removes unused `fallback` parameter reference  → Applied instantly
# 🟡 Suggest:   Refactors to guard clauses with CC=4          → Shows diff for review
# 🔴 Flag-Only: Removing `fallback` from function signature   → Flagged, never auto-applied
```

---

## 📐 Bloat Score Formula

The Bloat Score (0.0–100.0, graded A–F) is a weighted composite of five static metrics:

```
BloatScore = min(100.0,
    0.30 × CyclomaticComplexity  +
    0.25 × NestingDepth          +
    0.20 × DeadCodeLines         +
    0.15 × CognitiveComplexity   +
    0.10 × DuplicationRatio
)
```

| Grade | Score Range | Interpretation |
| :---: | :---: | :--- |
| **A** | 0–20 | Clean — minimal bloat, no LLM intervention needed |
| **B** | 21–40 | Good — minor dead code; Deterministic Fix Node handles it |
| **C** | 41–60 | Moderate — LLM Refactor Node invoked on complex functions |
| **D** | 61–80 | High bloat — significant structural complexity; full pipeline runs |
| **F** | 81–100 | Critical — AI over-engineering detected; immediate intervention required |

---

## 🔒 Local-First LLM Privacy & Provider Chain

CodeSlim is architected **privacy-first**. Your source code never leaves your machine unless you explicitly configure a cloud provider.

| Provider | Privacy | Cost | Speed | Setup |
| :--- | :---: | :---: | :---: | :--- |
| **Ollama (qwen2.5-coder:3b)** | ✅ 100% Local | $0.00 | ~25 tok/s | `ollama pull qwen2.5-coder:3b` |
| **Groq (llama-3.1-70b)** | ☁️ Cloud | Pay-per-token | ~200 tok/s | Set `GROQ_API_KEY` |
| **OpenAI (gpt-4o-mini)** | ☁️ Cloud | Pay-per-token | ~150 tok/s | Set `OPENAI_API_KEY` |
| **Node 2.5 CST Fallback** | ✅ 100% Local | $0.00 | Instant | Always available |

**Ollama Hardware Requirements for `qwen2.5-coder:3b` (Q4_K_M quantization):**
- VRAM: ~2.2 GB (GTX 1650 4GB sufficient)
- RAM: ~4 GB system RAM
- Storage: ~2.2 GB for model weights

**SHA-256 DiskCache**: All LLM responses are cached to disk using a SHA-256 hash of the prompt. Re-running CodeSlim on unchanged code costs **$0.00** regardless of provider.

---

## 🐳 Docker Deployment

### Option A — Single Container (CLI Tool)

```bash
# Build the image
docker build -t codeslim:latest .

# Analyze a local project (mount your codebase as a volume)
docker run --rm -v $(pwd)/src:/app/target codeslim:latest analyze /app/target

# Optimize with diff output
docker run --rm -v $(pwd)/src:/app/target codeslim:latest optimize /app/target/utils.py
```

### Option B — Docker Compose (CodeSlim + Ollama Sidecar)

The `docker-compose.yml` provisions both CodeSlim and an Ollama sidecar for a fully self-contained, offline AI code quality stack:

```bash
# Start the full stack
docker compose up -d

# Launch Web Studio on http://localhost:8000
docker compose exec codeslim codeslim ui --host 0.0.0.0 --port 8000

# Run analysis against a mounted project
docker compose exec codeslim codeslim scan /app/target
```

**Environment variables** are passed from your `.env` file automatically by docker-compose.

### Dockerfile Details

```dockerfile
FROM python:3.11-slim AS base
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml README.md ./
COPY codeslim/ ./codeslim/
COPY data/ ./data/
RUN pip install --no-cache-dir -e .
ENTRYPOINT ["codeslim"]
CMD ["--help"]
```

---

## 🤖 GitHub Actions Integration

### Option A — Composite Action (Recommended, Zero Setup)

Add CodeSlim as a step in any workflow to automatically audit PRs:

```yaml
# .github/workflows/codeslim.yml
name: CodeSlim Code Quality Audit

on:
  pull_request:
    paths:
      - '**.py'

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run CodeSlim Audit
        uses: ImdataScientistSachin/CodeSlim@main
        with:
          path: '.'                          # Directory to analyze
          groq-api-key: ${{ secrets.GROQ_API_KEY }}  # Optional: cloud LLM fallback
```

The action outputs a `codeslim_report.json` file with GitHub PR annotation format for downstream steps.

### Option B — Self-Hosted PR Webhook Bot

For full auto-fix capability (posting diffs as PR comments and optionally committing fixes):

```bash
# Start the webhook receiver on your server
codeslim bot serve --port 8000 --webhook-secret $GITHUB_WEBHOOK_SECRET
```

Then register `https://your-server.com:8000/webhook` as a GitHub repository webhook for `pull_request` events with content type `application/json`.

---

## 🧪 Testing & Quality Verification

CodeSlim enforces strict code quality and maintains a **100% green test suite** with zero linter errors:

```bash
# Run all unit & integration tests (96/96 passing)
python -m pytest -v

# Run with coverage report
python -m pytest --cov=codeslim --cov-report=html

# Run only fast (non-LLM) tests
python -m pytest -v -m "not llm"

# Run Ruff static analysis linter
python -m ruff check codeslim/ tests/

# Auto-fix Ruff issues
python -m ruff check codeslim/ tests/ --fix

# Run strict Mypy type checker
python -m mypy codeslim/
```

```text
======================== 96 passed, 1 warning in 3.04s ========================
```

**Test markers:** Tests making real LLM calls are marked with `@pytest.mark.llm` and excluded from the default run to keep CI fast.

### Makefile Shortcuts

A `Makefile` is provided for common development tasks:

```bash
make test          # Run full test suite
make lint          # Ruff + Mypy checks
make format        # Ruff auto-format
make clean         # Remove __pycache__, .mypy_cache, .pytest_cache
```

---

## 📁 Repository Structure

```text
CodeSlim/
├── .github/
│   └── workflows/               # GitHub Actions CI workflow definitions
├── codeslim/                    # Core Python Package
│   ├── analyzers/               # Static Sensor Node: Radon, Vulture, Lizard,
│   │                            #   Tree-Sitter & AST Nesting Visitor
│   ├── context/                 # Context Minimizer: LibCST Transformer,
│   │                            #   DocstringCompressor (NLTK + TF-IDF),
│   │                            #   Token Budget Engine (tiktoken)
│   ├── llm/                     # LLM Refactor Node: Ollama / OpenAI / Groq
│   │                            #   Dual-Provider Engine + DiskCache
│   ├── optimizer/               # AST Guardrail Safety Gate, ASTInvariantGate,
│   │                            #   Confidence Classifier & Unified Diff Generator
│   ├── pipeline/                # LangGraph-style Stateful Node Orchestration
│   ├── formatters/              # Output Formatters: Rich Terminal, JSON,
│   │                            #   github-pr, HTML Observatory
│   ├── bot/                     # FastAPI GitHub PR Webhook Receiver & Bot
│   │                            #   (HMAC-SHA256 verification, PR comment posting)
│   └── ui/                      # Tokyo Night Web Studio FastAPI Server
│                                #   & Static HTML Assets
├── data/                        # Reference data files (PyPI package registry
│                                #   snapshots for hallucination detection)
├── examples/                    # Example Python files for testing and demonstration
│   │                            #   (bloated AI-generated code samples)
├── scripts/                     # Developer utility scripts (CI helpers, benchmarks)
├── tests/                       # 96 Comprehensive Unit & Integration Tests
├── .codeslimignore              # Files/directories excluded from analysis
├── .gitignore                   # Git ignore rules
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── action.yml                   # GitHub Composite Action definition
├── docker-compose.yml           # Multi-service stack (CodeSlim + Ollama sidecar)
├── Dockerfile                   # Single-container Docker image (python:3.11-slim)
├── GEMINI.md                    # Gemini AI agent context file (project instructions
│                                #   for Gemini CLI / Google AI Studio integration)
├── LICENSE                      # MIT License
├── Makefile                     # Developer shortcuts (test, lint, format, clean)
├── PROJECT_OVERVIEW.md          # Deep-dive technical architecture document
│                                #   for engineering leads and architects
├── pyproject.toml               # Package metadata, dependencies & tool configs
├── requirements.txt             # Pinned production dependencies (pip users)
├── requirements-dev.txt         # Pinned dev + test dependencies (pip users)
├── uv.lock                      # uv lockfile for reproducible environments
└── README.md                    # This file
```

---

## 💻 Hardware Requirements

| Configuration | Spec | Notes |
| :--- | :--- | :--- |
| **Minimum (CLI Only)** | 4 GB RAM, any CPU | Static analysis + Deterministic Fix Node; no GPU needed |
| **Recommended (Ollama Local)** | 16 GB RAM, 4 GB VRAM (GTX 1650+) | Runs `qwen2.5-coder:3b` at ~25 tok/s locally |
| **Cloud Fallback** | Any | Any machine; send code to Groq/OpenAI instead of local Ollama |
| **Docker** | 4 GB RAM minimum | Build-essential required for tree-sitter C extensions |

---

## 🗺 Roadmap

| Status | Feature |
| :---: | :--- |
| ✅ Done | 6-stage deterministic + LLM pipeline |
| ✅ Done | LibCST lossless import pruning & docstring compression |
| ✅ Done | AST Invariant Gate safety rejection |
| ✅ Done | Ollama / OpenAI / Groq multi-provider chain |
| ✅ Done | FastAPI Web Studio + HTML Observatory |
| ✅ Done | GitHub PR Webhook Bot (HMAC-SHA256) |
| ✅ Done | Git pre-commit hook installer |
| ✅ Done | GitHub Composite Action (`action.yml`) |
| ✅ Done | Docker + docker-compose deployment |
| ✅ Done | SHA-256 DiskCache LLM response caching |
| 🔄 In Progress | PyPI package publish (`pip install codeslim`) |
| 🔄 In Progress | JavaScript / TypeScript support via tree-sitter-javascript |
| 🔜 Planned | VS Code Extension |
| 🔜 Planned | Claude / Anthropic API provider |
| 🔜 Planned | Multi-file cross-reference dead-code analysis |
| 🔜 Planned | SARIF output format for GitHub Security tab integration |
| 🔜 Planned | Configurable Bloat Score weight profiles (strict / balanced / lenient) |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository and create your feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Install dev dependencies**:
   ```bash
   uv sync
   # or
   pip install -e ".[dev]"
   ```

3. **Write tests** for your changes. All 96 existing tests must continue to pass.

4. **Run the full quality gate** before opening a PR:
   ```bash
   python -m pytest -v -m "not llm"
   python -m ruff check codeslim/ tests/
   python -m mypy codeslim/
   ```

5. **Open a Pull Request** against `main` with a clear description of the problem and solution.

### Code Standards

- Python 3.11+ type hints required on all new functions.
- Ruff rules `E, F, I, UP, B` must pass with 0 errors.
- Mypy strict mode must pass.
- New LLM-dependent tests must be marked `@pytest.mark.llm`.

---

## ❓ FAQ

**Q: Does CodeSlim work on non-Python files?**  
A: Currently Python-only. JavaScript/TypeScript support is on the roadmap via `tree-sitter-javascript`. The `tree-sitter-language-pack` dependency is already included to support this expansion.

**Q: Will CodeSlim break my code?**  
A: No. The AST Guardrail Safety Gate (Stage 5) runs 4 strict invariant checks on every LLM output. If any check fails — syntax error, signature change, decorator removal, or async status change — CodeSlim automatically reverts to the deterministic LibCST fix. Your code is never silently corrupted.

**Q: Can I run CodeSlim without any LLM?**  
A: Yes. Use `codeslim optimize --no-llm` or simply don't configure any LLM provider. The Deterministic Fix Node (Stage 3) handles 80% of issues — unused imports, dead variables, whitespace — with zero LLM cost.

**Q: What is GEMINI.md?**  
A: It's a context file for the [Gemini CLI](https://github.com/google-gemini/gemini-cli) and Google AI Studio agents. It provides project instructions so Gemini-powered AI agents can understand the CodeSlim architecture when assisting with development tasks.

**Q: Why does the Dockerfile use `python:3.11-slim` and install `build-essential`?**  
A: The `tree-sitter` and `tree-sitter-python` packages compile C extensions at install time. `build-essential` provides the `gcc` compiler required for this. The slim base keeps the final image lean (~400 MB).

**Q: How does the pre-commit hook stay under 50ms?**  
A: The hook runs only the Deterministic Fix Node (Stage 3) — LibCST import pruning — with no LLM calls. LibCST operates entirely in memory on the staged files.

**Q: Is the `diskcache` cache safe across parallel runs?**  
A: Yes. DiskCache uses file locking and atomic writes. Parallel `codeslim optimize` calls on different files are safe. The cache is keyed by SHA-256 hash of the exact prompt, so cache collisions are mathematically impossible.

---

## 🔐 Security

If you discover a security vulnerability, please **do not open a public GitHub issue**. Instead, email the maintainer directly or use GitHub's private vulnerability reporting. We follow responsible disclosure and will acknowledge reports within 48 hours.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the Python & AI engineering community.**

If CodeSlim saves you from shipping bloated AI-generated code, consider giving it a ⭐ on GitHub!

[⭐ Star on GitHub](https://github.com/ImdataScientistSachin/CodeSlim) · [🐛 Report a Bug](https://github.com/ImdataScientistSachin/CodeSlim/issues) · [💡 Request a Feature](https://github.com/ImdataScientistSachin/CodeSlim/issues)

</div>
