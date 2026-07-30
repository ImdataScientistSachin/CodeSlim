<div align="center">

<!-- ANIMATED HEADER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:00ff88,100:6e40c9&height=220&section=header&text=CodeSlim&fontSize=80&fontColor=ffffff&fontAlignY=38&desc=Agentic%20AI%20Code%20Quality%20Audit%20%E2%80%A2%20Context%20Minimizer%20%E2%80%A2%20Guardrail%20Engine&descAlignY=58&descSize=17&animation=fadeIn" width="100%"/>

<!-- TYPING ANIMATION -->
[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&duration=3000&pause=800&color=00FF88&center=true&vCenter=true&multiline=true&width=860&height=80&lines=76%25+token+reduction+%C2%B7+%240.00+LLM+cost+for+80%25+of+fixes+%C2%B7+0%25+hallucination+corruption;6-Stage+LangGraph+DAG+%C2%B7+LibCST+%C2%B7+AST+Safety+Gate+%C2%B7+Ollama+%2F+OpenAI+%2F+Groq;The+automated+guardrail+between+AI+code+generation+and+production+%F0%9F%9B%A1%EF%B8%8F)](https://git.io/typing-svg)

<br/>

<!-- PRIMARY QUALITY BADGES -->
[![Python Version](https://img.shields.io/badge/python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![CI Tests](https://img.shields.io/github/actions/workflow/status/ImdataScientistSachin/CodeSlim/ci.yml?branch=main&label=96%2F96%20Tests&style=for-the-badge&logo=pytest&logoColor=white&color=2ea44f)](#-testing--quality-verification)
[![LangGraph Pipeline](https://img.shields.io/badge/LangGraph-Multi--Agent%20Pipeline-6e40c9?style=for-the-badge&logo=diagramsdotnet&logoColor=white)](#-architecture--6-stage-pipeline)
[![LLM Runtime](https://img.shields.io/badge/LLM-Ollama%20%7C%20OpenAI%20%7C%20Groq-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)](#-local-first-llm-privacy--provider-chain)
[![Ruff & Mypy](https://img.shields.io/badge/Ruff%20%7C%20Mypy-0%20errors-000000?style=for-the-badge&logo=ruff&logoColor=white)](#-testing--quality-verification)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](#-docker-deployment)
[![GitHub Action](https://img.shields.io/badge/GitHub_Action-Available-181717?style=for-the-badge&logo=github-actions&logoColor=white)](#-github-actions-integration)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

<br/>

<!-- SOCIAL PROOF BADGES -->
[![Star on GitHub](https://img.shields.io/github/stars/ImdataScientistSachin/CodeSlim?style=for-the-badge&logo=github&color=6e40c9&logoColor=white&label=%E2%AD%90%20Stars)](https://github.com/ImdataScientistSachin/CodeSlim)
[![Fork](https://img.shields.io/github/forks/ImdataScientistSachin/CodeSlim?style=for-the-badge&logo=github&color=00ff88&logoColor=black&label=%F0%9F%8D%B4%20Forks)](https://github.com/ImdataScientistSachin/CodeSlim/fork)
[![Issues](https://img.shields.io/github/issues/ImdataScientistSachin/CodeSlim?style=for-the-badge&logo=github&color=FF6B6B&logoColor=white&label=%F0%9F%90%9B%20Issues)](https://github.com/ImdataScientistSachin/CodeSlim/issues)
[![PyPI](https://img.shields.io/badge/PyPI-Coming_Soon-FF6B6B?style=for-the-badge&logo=pypi&logoColor=white)](https://github.com/ImdataScientistSachin/CodeSlim)

<br/>

> **CodeSlim** is a deterministic-first, open-source **Agentic AI CLI Engine** that sits between Python codebases and Large Language Models. It combines fast C-native static analysis sensors (Radon, Vulture, Lizard, Tree-Sitter) with LibCST Concrete Syntax Trees to slash token bloat by up to **76%**, while enforcing **AST syntax guardrails** to prevent LLM hallucinations from ever corrupting your source code.

**[⚡ Quick Start](#-quick-start)** &nbsp;·&nbsp; **[💻 CLI Commands](#-cli-commands--usage)** &nbsp;·&nbsp; **[🏗️ Architecture](#-architecture--6-stage-pipeline)** &nbsp;·&nbsp; **[🐳 Docker](#-docker-deployment)** &nbsp;·&nbsp; **[🤖 GitHub Action](#-github-actions-integration)** &nbsp;·&nbsp; **[🤝 Contributing](#-contributing)**

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

AI models generate code token-by-token, optimizing for _"Does this satisfy the prompt?"_ — not _"Is this the minimum viable expression of logic?"_ This creates four production-grade vulnerabilities:

1. **Defensible Bloat** — 50 lines where 10 standard-library lines suffice; every individual line compiles, but the whole is unnecessary.
2. **Defensive Nesting Hell** — Cascading `if-else` structures (6–10 levels deep) instead of guard clauses and early returns.
3. **Package Hallucinations** — AI models import non-existent or deprecated packages (`from sklearn_extra import FastData`).
4. **Over-Abstraction** — Complex class hierarchies, interface wrappers, and factory patterns for single-use functions.

### 📊 Industry Benchmark Data (2025–2026)

| Metric | Benchmark | Source | Impact |
| :----- | :-------- | :----- | :----: |
| **Defect Multiplier** | AI-generated code has **1.7× more bugs** than human code | CodeRabbit 2026 | 🔴 Critical |
| **Code Duplication** | AI code exhibits **up to 8× more duplication** | Pure Math AI | 🔴 Critical |
| **Developer Trust Gap** | **96% of engineers** distrust unverified AI code | Sonar / Stack Overflow 2026 | 🔴 Critical |
| **PR Size Inflation** | Average PR size grew **154%** post-AI adoption | Google DORA 2025 | 🟡 Major |
| **Hallucination Rate** | **5.2–21.7%** of AI package suggestions are non-existent | USENIX Security 2025 | 🔴 Critical |
| **CodeSlim Reduction** | Production reduction of **31.7% LOC** achieved | Internal Benchmarks | ✅ Proven |

---

## 🌟 Key Capabilities

> [!IMPORTANT]
> **Deterministic First, AI Second**: 80% of dead-code purging and import pruning is performed with **100% mathematical precision** via LibCST — zero LLM cost. The LLM is invoked strictly on pre-minimized, complex function chunks.

| Feature | Description | Impact |
| :------ | :---------- | :----- |
| ⚡ **Lossless Context Pruning** | Strips non-essential docstrings and dead blocks via LibCST + C-Native Tree-Sitter (`tree-sitter>=0.26.0`). | **Up to 76% Token Reduction** |
| 🛡️ **AST Syntax Safety Gate** | Validates `ast.parse()` syntax and enforces public class/function signature & decorator preservation. | **0% Hallucination Corruption** |
| ⚙️ **Deterministic Fix Node** | Auto-purges unused imports and dead variables without calling LLMs. | **$0.00 LLM Cost for 80% of Fixes** |
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
| :--- | :------- | :------------------------ | :----------------- |
| **Ruff / Flake8** | Syntax & style linting | Passes bloated AI code because syntax is valid | Detects structural bloat, cognitive nesting depth & hallucinated APIs |
| **SonarQube** | Rule-based code smells | Ignores task intent and fabricated package references | Integrates AST sensors + multi-stage hallucination verification |
| **CodeRabbit / Qodo** | AI PR review comments | Posts text comments; cannot rewrite or minimize source code | Generates behavior-preserving code rewrites with verified unified diffs |
| **DepScope** | Standalone import scanner | Scans imports only; no code minimization or refactoring | Integrates registry lookups into the full 4-stage optimizer pipeline |
| **Pylint** | General code quality | No AI-specific bloat heuristics | Tuned Bloat Score formula targeting AI generation patterns specifically |

<div align="center">

<br/>

**If CodeSlim catches one hallucinated import before it hits production, it's already paid for itself.**

[![⭐ Star CodeSlim on GitHub](https://img.shields.io/badge/⭐_Star_CodeSlim-on_GitHub-6e40c9?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ImdataScientistSachin/CodeSlim)
[![🍴 Fork & Contribute](https://img.shields.io/badge/🍴_Fork_%26-Contribute-00ff88?style=for-the-badge&logo=github&logoColor=black)](https://github.com/ImdataScientistSachin/CodeSlim/fork)

<br/>

</div>

---

## 🛠 Tech Stack

### Core Pipeline & Analysis Layer

| Library | Version | Role |
| :------ | :------ | :--- |
| **LibCST** | `>=1.4` | Lossless Concrete Syntax Tree transformer — dead-code pruning, import removal, docstring stripping without altering formatting |
| **tree-sitter** | `>=0.26.0,<0.27.0` | C-native AST parser for sub-10ms skeleton extraction |
| **tree-sitter-python** | `==0.25.0` | Python grammar bindings for Tree-Sitter |
| **tree-sitter-language-pack** | `>=1.12.0,<2.0.0` | Multi-language grammar pack (future polyglot support) |
| **Python ast** | stdlib | `ast.parse()` syntax validation in the AST Guardrail Safety Gate |
| **Radon** | `>=6.0` | Cyclomatic Complexity (CC), Maintainability Index (MI), Raw LOC metrics |
| **Vulture** | `>=2.7` | Dead code detection, unused import scanning (min_conf ≥ 80) |
| **Lizard** | `>=1.18` | Cognitive Complexity and NLOC (Non-Comment Lines of Code) |

### LLM, NLP & Orchestration

| Library | Version | Role |
| :------ | :------ | :--- |
| **LangGraph** | `>=1.2.0,<2.0.0` | Stateful multi-node pipeline orchestration (graph-style agentic DAG) |
| **OpenAI SDK** | `>=1.0` | OpenAI Cloud provider fallback (`gpt-4o-mini`) |
| **httpx** | `>=0.27` | Async HTTP client for Ollama local API & Groq API |
| **tiktoken** | `>=0.5` | Token counting and budget enforcement via `cl100k_base` encoding |
| **diskcache** | `>=5.6` | SHA-256 keyed on-disk LLM response caching |
| **NLTK** | `>=3.8` | Tokenization and sentence splitting for `DocstringCompressor` |
| **scikit-learn** | `>=1.4` | TF-IDF score ranking to extract top-k informative sentences |

### API, CLI & Quality Tooling

| Library | Version | Role |
| :------ | :------ | :--- |
| **FastAPI** | `>=0.110` | Web Studio UI server, GitHub PR Webhook receiver, and REST API |
| **Click** | `>=8.0` | CLI command parsing and entrypoint (`codeslim` command) |
| **Rich** | `>=13.0` | Tokyo Night themed terminal dashboards, progress bars, output tables |
| **Pydantic** | `>=2.0` | Data validation and typed schema models throughout the pipeline |
| **pydantic-settings** | `>=2.0` | `.env` file loading and environment variable configuration |
| **structlog** | `>=24.0` | Structured JSON-compatible logging throughout all pipeline stages |
| **pytest** | `>=8.0` | Unit and integration test runner (96/96 passing) |
| **Ruff** | `>=0.4` | Blazing-fast linter (E, F, I, UP, B rules; 120 char line length) |
| **Mypy** | `>=1.10` | Strict static type checking (`python_version = "3.11"`) |
| **uv** | latest | Recommended ultra-fast package manager and environment sync |

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

CodeSlim processes code through a deterministic **6-stage agentic pipeline** orchestrated as a **LangGraph stateful DAG**:

```text
  INPUT → .py file / directory / GitHub PR Webhook
  │
  ├─ Stage 1 · STATIC SENSOR NODE    (codeslim/analyzers/)
  │   • Radon — Cyclomatic Complexity (CC), Maintainability Index (MI)
  │   • Vulture — Dead code & unused imports (min_conf ≥ 80)
  │   • Lizard — Cognitive Complexity & NLOC
  │   • Tree-Sitter — C-Native AST skeleton extraction (<10ms)
  │   • AST Visitor — Nesting depth & import classification
  │   • MD5 Duplication — Token-hash sliding window
  │   └─ Output: FileMetrics & BloatMap
  │
  ├─ Stage 2 · CONTEXT MINIMIZER NODE    (codeslim/context/)
  │   • LibCST Lossless Transformer — strips docstrings & dead blocks
  │   • DocstringCompressor — NLTK tokenize + TF-IDF top-k ranking
  │   • tiktoken Budget Enforcer — cl100k_base token counting
  │   • Bloat Score Calculation — 0.0 to 100.0 Grade A–F
  │   └─ Output: Pruned Code + Bloat Score
  │
  ├─ Stage 3 · DETERMINISTIC FIX NODE    ← $0.00 LLM Cost
  │   • LibCST auto-purge unused imports & dead variables
  │   • SHA-256 DiskCache — skips re-processing unchanged files
  │   • 100% deterministic — 0% hallucination risk
  │   └─ Output: Cleaned Source
  │
  ├─ Stage 4 · CHUNKED LLM REFACTOR NODE    (codeslim/llm/)
  │   • Extracts only complex functions (CC > 10)
  │   • Provider chain: Ollama → OpenAI → Groq → Node 2.5 CST
  │   • Refactors nested logic into clean guard clauses
  │   • Response cached by SHA-256 hash via DiskCache
  │   └─ Output: Proposed Refactored Code
  │
  ├─ Stage 5 · AST GUARDRAIL SAFETY GATE    (codeslim/optimizer/)
  │   • ast.parse() syntax verification
  │   • Public class & function signature set preservation
  │   • Decorator preservation (@staticmethod, @classmethod)
  │   • Coroutine status preservation (async def → async def)
  │   • Safety Rejection: reverts broken LLM code to CST fix
  │   • Always-On Unified Diff Generator
  │   └─ Output: Verified Safe Code + Unified Diff
  │
  └─ Stage 6 · FORMATTERS & OBSERVATORY UI    (codeslim/formatters/)
      • Rich Terminal Dashboard (Tokyo Night Theme)
      • Standalone HTML Observatory with Surgery Modal
      • FastAPI Web Studio UI & GitHub PR Webhook Receiver
      • JSON / github-pr structured output formats
      └─ Output: Final Report
```

### LangGraph Orchestration

The pipeline stages are wired as a **LangGraph stateful DAG**. Each node receives the shared `PipelineState` TypedDict, transforms it, and passes control to the next node. The graph handles:
- **Conditional branching** — skips the LLM Refactor Node when `CC ≤ 10` (cost optimization)
- **Circuit-breaking** — falls back to the Deterministic Fix Node when the AST Gate rejects LLM output

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

**Option D — Docker (zero local setup)**

```bash
# Analyze a project immediately — no Python install required
docker run --rm -v $(pwd)/src:/app/target ghcr.io/imdatascientistsachin/codeslim:latest analyze /app/target
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your preferred LLM provider (Ollama is default — free & offline)
```

### 3. Pull Local LLM (Optional but Recommended)

```bash
# Start Ollama server
ollama serve

# Pull the default local model (~2.2 GB, runs on GTX 1650 4GB)
ollama pull qwen2.5-coder:3b
```

> [!TIP]
> **Zero Cloud Cost**: With Ollama running, CodeSlim operates 100% offline. No API keys required for the full pipeline.

### 4. Run Your First Analysis

```bash
# Analyze the CodeSlim codebase itself (no LLM calls — purely static)
codeslim analyze ./codeslim/ --format rich

# Full optimization pipeline on a single file
codeslim optimize ./codeslim/analyzers/radon_analyzer.py

# Export a standalone HTML Observatory report
codeslim scan ./codeslim/ --export-html observatory_report.html
```

### 🎬 See It In Action

> **To see the Tokyo Night Rich terminal dashboard**, run:
> ```bash
> codeslim scan ./codeslim/ --format rich
> ```
> The dashboard renders color-coded bloat scores (Grade A–F), cyclomatic complexity heatmaps, dead-code flagging, and a per-file summary table — all in your terminal.
>
> **To see the HTML Observatory**, open `observatory_report.html` in any browser after running `codeslim scan --export-html`. It's a fully standalone, zero-server interactive report with a code diff surgery modal.

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

# Optimize without LLM (deterministic CST only — $0 cost)
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
LLM_MODEL_ANALYSIS=qwen2.5-coder:3b
LLM_MODEL_OPTIMIZATION=qwen2.5-coder:3b

# ─── Ollama Local Configuration ───────────────────────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434

# ─── OpenAI Cloud Configuration (optional fallback) ───────────────────────────
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# ─── Groq Cloud Configuration (optional, fast inference) ──────────────────────
GROQ_API_KEY=gsk_...
GROQ_MODEL=ollama-3.1-70b-versatile

# ─── GitHub PR Bot Configuration ──────────────────────────────────────────────
GITHUB_TOKEN=ghp_...
GITHUB_WEBHOOK_SECRET=your-webhook-secret

# ─── Pipeline Thresholds ──────────────────────────────────────────────────────
CC_THRESHOLD=10                 # Minimum CC to trigger LLM refactoring
VULTURE_MIN_CONFIDENCE=80       # Minimum Vulture confidence to flag dead code
MAX_TOKEN_BUDGET=4096           # Maximum token budget per file chunk sent to LLM

# ─── Caching ──────────────────────────────────────────────────────────────────
CACHE_DIR=.codeslim_cache       # SHA-256 keyed DiskCache LLM response storage
```

### LLM Provider Priority Chain

```
  codeslim optimize target.py
              │
              ▼
    Ollama running locally?
          /         \
        YES           NO
        /               \
       ▼                 ▼
  Ollama Local       OpenAI API key set?
  qwen2.5-coder:3b     /          \
  (Private & Free)   YES            NO
                      /               \
                     ▼                 ▼
             OpenAI gpt-4o-mini   Groq API key set?
                                    /         \
                                  YES           NO
                                  /               \
                                 ▼                 ▼
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

The Bloat Score (0.0–100.0, graded A–F) is a **weighted composite of five static metrics**:

```
BloatScore = min(100.0,
    0.30 × CyclomaticComplexity  +   ← primary driver (Radon CC)
    0.25 × NestingDepth          +   ← AI nesting-hell detector
    0.20 × DeadCodeLines         +   ← Vulture-detected bloat
    0.15 × CognitiveComplexity   +   ← Lizard NLOC sensor
    0.10 × DuplicationRatio          ← MD5 token-hash sliding window
)
```

| Grade | Score Range | Interpretation |
| :---: | :---------: | :------------- |
| **A** | 0–20 | Clean — minimal bloat, no LLM intervention needed |
| **B** | 21–40 | Good — minor dead code; Deterministic Fix Node handles it |
| **C** | 41–60 | Moderate — LLM Refactor Node invoked on complex functions |
| **D** | 61–80 | High bloat — significant structural complexity; full pipeline runs |
| **F** | 81–100 | Critical — AI over-engineering detected; immediate intervention required |

---

## 🔒 Local-First LLM Privacy & Provider Chain

CodeSlim is architected **privacy-first**. Your source code never leaves your machine unless you explicitly configure a cloud provider.

| Provider | Privacy | Cost | Speed | Setup |
| :------- | :-----: | :--: | :---: | :---- |
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

# Export HTML Observatory
docker run --rm -v $(pwd)/src:/app/target -v $(pwd)/out:/app/out \
  codeslim:latest scan /app/target --export-html /app/out/report.html
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
      - "**.py"

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run CodeSlim Audit
        uses: ImdataScientistSachin/CodeSlim@main
        with:
          path: "."                                       # Directory to analyze
          groq-api-key: ${{ secrets.GROQ_API_KEY }}      # Optional: cloud LLM fallback
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

# Run only fast (non-LLM) tests — ideal for CI
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
├── data/                        # Reference data: PyPI registry snapshots
│                                #   for hallucination detection
├── examples/                    # Bloated AI-generated code samples for demos
├── scripts/                     # Developer utility scripts & CI helpers
├── tests/                       # 96 Comprehensive Unit & Integration Tests
├── .codeslimignore              # Files/directories excluded from analysis
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── action.yml                   # GitHub Composite Action definition
├── docker-compose.yml           # Multi-service stack (CodeSlim + Ollama sidecar)
├── Dockerfile                   # Single-container Docker image (python:3.11-slim)
├── GEMINI.md                    # AI agent context file for Gemini CLI integration
├── LICENSE                      # MIT License
├── Makefile                     # Developer shortcuts (test, lint, format, clean)
├── PROJECT_OVERVIEW.md          # Deep-dive technical architecture document
├── pyproject.toml               # Package metadata, dependencies & tool configs
├── requirements.txt             # Pinned production dependencies (pip users)
├── requirements-dev.txt         # Pinned dev + test dependencies (pip users)
└── uv.lock                      # uv lockfile for reproducible environments
```

---

## 💻 Hardware Requirements

| Configuration | Spec | Notes |
| :------------ | :--- | :---- |
| **Minimum (CLI Only)** | 4 GB RAM, any CPU | Static analysis + Deterministic Fix Node; no GPU needed |
| **Recommended (Ollama Local)** | 16 GB RAM, 4 GB VRAM (GTX 1650+) | Runs `qwen2.5-coder:3b` at ~25 tok/s locally |
| **Cloud Fallback** | Any | Any machine; send code to Groq/OpenAI instead of Ollama |
| **Docker** | 4 GB RAM minimum | build-essential required for tree-sitter C extensions |

---

## 🗺 Roadmap

| Status | Feature |
| :----: | :------ |
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

- Python 3.11+ type hints required on all new functions
- Ruff rules `E, F, I, UP, B` must pass with 0 errors
- Mypy strict mode must pass
- New LLM-dependent tests must be marked `@pytest.mark.llm`
- Google-style docstrings with `Args:`, `Returns:`, `Raises:` on all public functions

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

**Q: What happens if the LLM returns invalid JSON or malformed code?**
A: CodeSlim uses Pydantic V2 schema validation (`LLMRefactorResponse`) on every LLM completion. On JSON parse failure, it applies escalating prompt feedback (up to 3 retries). If all retries fail, Stage 5 rejects the output and Stage 3's deterministic CST fix is applied instead — guaranteed safe output regardless of LLM quality.

---

## 🔐 Security

If you discover a security vulnerability, please **do not open a public GitHub issue**. Instead, email the maintainer directly or use GitHub's private vulnerability reporting. We follow responsible disclosure and will acknowledge reports within 48 hours.

**Security guarantees built into the pipeline:**
- No `eval()`, `exec()`, or `shell=True` anywhere in the codebase
- All LLM responses validated through Pydantic V2 before any code mutation
- HMAC-SHA256 signature verification on all GitHub webhook payloads
- File paths sanitized with `pathlib.Path` — no string concatenation

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the Python & AI engineering community.**

*The AI coding explosion demands automated guardrails. CodeSlim is that guardrail.*

<br/>

[![⭐ Star on GitHub](https://img.shields.io/badge/⭐_Star_on_GitHub-CodeSlim-6e40c9?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ImdataScientistSachin/CodeSlim)
[![🐛 Report a Bug](https://img.shields.io/badge/🐛_Report-a_Bug-FF6B6B?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ImdataScientistSachin/CodeSlim/issues)
[![💡 Request a Feature](https://img.shields.io/badge/💡_Request-a_Feature-00ff88?style=for-the-badge&logo=github&logoColor=black)](https://github.com/ImdataScientistSachin/CodeSlim/issues)
[![🤝 Contribute](https://img.shields.io/badge/🤝_Open-a_PR-2496ED?style=for-the-badge&logo=github&logoColor=white)](https://github.com/ImdataScientistSachin/CodeSlim/fork)

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6e40c9,50:00ff88,100:0d1117&height=120&section=footer" width="100%"/>

</div>
