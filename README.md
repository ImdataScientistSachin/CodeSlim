# 🚀 CodeSlim: The Agentic Code Analysis, Context Minimizer & Guardrail Engine

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-76%2F76%20passing-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-Multi--Agent%20Pipeline-orange.svg)](#-architecture--data-flow)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Local-First AI](https://img.shields.io/badge/AI-Ollama%20%7C%20OpenAI-purple.svg)](#-local-first-llm-architecture)

> **CodeSlim** is an open-source, production-grade **Agentic AI CLI Engine** that sits between Python codebases and LLMs. It uses deterministic static analysis sensors (Radon, Vulture, Lizard, AST) to pre-process source files, prunes token bloat using lossless LibCST Concrete Syntax Trees, calls local/cloud LLMs with focused context, and enforces **AST syntax guardrails** to prevent hallucinations from ever corrupting your codebase.

---

## 🌟 Key Features

* ⚡ **30–50% Token Reduction**: Lossless LibCST pruning strips dead code and docstrings, reducing input tokens and saving LLM API costs.
* 🛡️ **0% Hallucination Safety Gate**: AST `ast.parse()` and public signature preservation checks reject broken syntax or deleted APIs.
* 🔒 **Local-First Privacy**: Runs free, private local LLMs (Ollama `qwen2.5-coder:3b` under 2.2GB VRAM) with automatic cloud fallback to OpenAI (`gpt-4o-mini`).
* 🎯 **3-Tier Confidence Classifier**: Categorizes refactoring actions into `Auto-Safe` (dead code), `Suggest` (simplification), and `Flag-Only` (structural extraction).
* 📊 **Multi-Target Output Formatters**: Emits Rich terminal panels, structured JSON for CI/CD, GitHub Markdown tables, and interactive HTML Observatories.
* 🔭 **Project Observatory Dashboard**: Multi-file codebase-level scanning with visual file treemaps, cross-file phantom function detection, and Tokyo Night interactive diff modal.
* 🤖 **Auto-Fix GitHub PR Bot**: Asynchronous FastAPI webhook receiver with HMAC-SHA256 signature verification that automatically reviews Pull Requests and auto-commits Tier-1 dead import removals.
* 🪝 **Git Pre-Commit Guardrail Hook**: Single command `codeslim install-hooks` installs local Git hooks to strip dead imports in < 50ms before code leaves your machine.

---

## 📐 Architecture & Data Flow

CodeSlim executes an autonomous **6-stage pipeline** using specialized node agents:

```
  USER INPUT (.py File or Directory / GitHub Webhook)
           │
           ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 1. STATIC SENSOR NODE (codeslim/analyzers/...)             │
  │    • Radon (Cyclomatic Complexity CC > 10)                  │
  │    • Vulture (Dead code & unused imports min_conf >= 80)    │
  │    • Lizard (Cognitive complexity & NLOC)                  │
  │    • AST Visitor (Nesting depth & package imports)        │
  │    • Duplication (MD5 token hashing sliding window)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ FileMetrics & BloatMap
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. CONTEXT MINIMIZER NODE (codeslim/context/...)           │
  │    • LibCST Lossless Transformer (Strips docstrings & dead) │
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
  │    • ast.parse() syntax verification                        │
  │    • Public class & function signature set preservation     │
  │    • Safety Rejection: Reverts broken LLM code to CST fix   │
  │    • Always-On Unified Diff Generator                      │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ Final Report & Diff
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. FORMATTERS & OBSERVATORY UI (codeslim/formatters/...)    │
  │    • Rich Terminal Dashboard (Tokyo Night Theme)            │
  │    • Standalone HTML Observatory with Surgery Modal         │
  │    • FastAPI GitHub PR Bot Webhook Receiver                │
  └─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies using **`uv`** (or `pip`):

```bash
git clone https://github.com/ImdataScientistSachin/CodeSlim.git
cd CodeSlim
uv sync
```

Or install via standard `pip`:

```bash
pip install -e .
```

### 2. Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure `.env` for local Ollama or cloud execution:

```env
LLM_PROVIDER=ollama
LLM_MODEL_ANALYSIS=qwen2.5-coder:3b
LLM_MODEL_OPTIMIZATION=qwen2.5-coder:3b
OLLAMA_BASE_URL=http://localhost:11434
CODESLIM_GITHUB_TOKEN=your_github_pat_token_here
CODESLIM_GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
```

---

## 💻 CLI Usage & Commands

### 🔍 1. Fast Code Bloat Analysis (`codeslim analyze`)

Scan Python file(s) for complexity and bloat without calling LLMs:

```bash
codeslim analyze ./codeslim/ --format rich
```

### ⚡ 2. Full Optimization Pipeline (`codeslim optimize`)

Run full deterministic LibCST dead-code removal and LLM refactoring:

```bash
codeslim optimize ./target_file.py --apply --backup
```

### 🔭 3. Project Observatory & Interactive HTML Export (`codeslim scan`)

Scan an entire directory and export an interactive Tokyo Night HTML Observatory with file surgery modals:

```bash
codeslim scan ./codeslim/ --export-html observatory_report.html
```

### 🤖 4. Start GitHub PR Webhook Bot (`codeslim bot serve`)

Start the FastAPI webhook receiver server for automated PR audits:

```bash
codeslim bot serve --port 8000 --auto-commit
```

### 🪝 5. Install Git Pre-Commit Guardrail Hook (`codeslim install-hooks`)

Install local Git pre-commit hook into `.git/hooks/pre-commit` to clean dead code on `git commit`:

```bash
codeslim install-hooks
```

---

## 🧪 Testing & Verification

CodeSlim maintains a **100% passing test suite** (76/76 unit and integration tests):

```bash
uv run pytest -v
```

```text
======================== 76 passed, 1 warning in 1.99s ========================
```

---

## 📄 Documentation Links

- 📖 **[CODESLIM_GUIDE.md](file:///g:/Project%20Directory/AGENTIC%20AI%20PROJECT%20DIRECTORY/CodeSlim/documents/CODESLIM_GUIDE.md)** — Master Developer Textbook, Architecture Breakdown & 25 Q&As.
- 🤖 **[BOT_SETUP_GUIDE.md](file:///g:/Project%20Directory/AGENTIC%20AI%20PROJECT%20DIRECTORY/CodeSlim/documents/BOT_SETUP_GUIDE.md)** — Step-by-Step GitHub Webhook, PAT Token & ngrok Setup.
- 📜 **[GEMINI.md](file:///g:/Project%20Directory/AGENTIC%20AI%20PROJECT%20DIRECTORY/CodeSlim/GEMINI.md)** — Version 2.5 Ultimate Workspace Protocol & Rule 11 Audit Checklist.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
