# 🚀 CodeSlim: Agentic Code Quality Audit, Context Minimizer & Guardrail Engine

[![Python Version](https://img.shields.io/badge/python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-96%2F96%20passing-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)](#-testing--quality-verification)
[![Architecture](https://img.shields.io/badge/architecture-Multi--Agent%20Pipeline-orange?style=for-the-badge&logo=diagramsdotnet&logoColor=white)](#-architecture--pipeline-data-flow)
[![Code Style](https://img.shields.io/badge/code%20style-Ruff%20%7C%20Mypy-000000?style=for-the-badge&logo=ruff&logoColor=white)](#-testing--quality-verification)
[![Local-First AI](https://img.shields.io/badge/AI-Ollama%20%7C%20OpenAI-8A2BE2?style=for-the-badge&logo=openai&logoColor=white)](#-local-first-llm-privacy)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

> **CodeSlim** is a deterministic-first, open-source **Agentic AI CLI Engine** that sits between Python codebases and Large Language Models. It combines fast C-native static analysis sensors (Radon, Vulture, Lizard, Tree-Sitter) with LibCST Concrete Syntax Trees to slash token bloat by up to **76%**, while enforcing **AST syntax guardrails** to prevent LLM hallucinations from ever corrupting your source code.

---

## 🌟 Key Capabilities

> [!IMPORTANT]
> **Deterministic First, AI Second**: 80% of dead-code purging and import pruning is performed with **100% mathematical precision** via LibCST with **zero LLM cost**. The LLM is invoked strictly on pre-minimized, complex function chunks.

| Feature | Description | Impact |
| :--- | :--- | :--- |
| ⚡ **Lossless Context Pruning** | Strips non-essential docstrings and dead blocks via LibCST + C-Native Tree-Sitter (`tree-sitter>=0.26.0`). | **Up to 76% Token Reduction** |
| 🛡️ **AST Syntax Safety Gate** | Validates `ast.parse()` syntax and enforces public class/function signature & decorator preservation. | **0% Hallucination Corruption** |
| ⚡ **Deterministic Fix Node** | Auto-purges unused imports and dead variables without calling LLMs. | **$0.00 LLM Cost for 80% of Fixes** |
| 🔒 **Local-First Privacy** | Runs 100% local, offline LLMs via Ollama (`qwen2.5-coder:3b`) with optional cloud fallback. | **Complete Code Privacy** |
| 🎯 **3-Tier Confidence Engine** | Categorizes refactor actions into `Auto-Safe`, `Suggest`, and `Flag-Only` tiers. | **Zero Unintended Breaking Changes** |
| 🔭 **HTML Observatory UI** | Generates standalone Tokyo Night interactive dashboards with code diff surgery modals. | **Instant Codebase Visibility** |
| 🤖 **Auto-Fix GitHub PR Bot** | Asynchronous FastAPI webhook receiver with HMAC-SHA256 verification for automated PR audits. | **Automated CI/CD Code Review** |
| 🪝 **Git Pre-Commit Hook** | Installs lightweight pre-commit guardrails to strip dead code in < 50ms before committing. | **Shift-Left Quality Enforcement** |

---

## 📐 Architecture & Pipeline Data Flow

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
  │    • Duplication (MD5 token hashing sliding window)        │
  └──────────────────────────────┬──────────────────────────────┘
                                 │ FileMetrics & BloatMap
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 2. CONTEXT MINIMIZER NODE (codeslim/context/...)           │
  │    • LibCST Lossless Transformer (Strips docstrings & dead) │
  │    • DocstringCompressor (Summarizes long docstrings)       │
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
                                 │ Final Report & Unified Diff
                                 ▼
  ┌─────────────────────────────────────────────────────────────┐
  │ 6. FORMATTERS & OBSERVATORY UI (codeslim/formatters/...)    │
  │    • Rich Terminal Dashboard (Tokyo Night Theme)            │
  │    • Standalone HTML Observatory with Surgery Modal         │
  │    • FastAPI Web Studio UI & GitHub Webhook Receiver        │
  └──────────────────────────────┴──────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Installation

Clone the repository and install using **`uv`** (recommended) or standard `pip`:

```bash
# Clone the repository
git clone https://github.com/ImdataScientistSachin/CodeSlim.git
cd CodeSlim

# Sync dependencies with uv
uv sync

# Or install via editable pip
pip install -e .
```

### 2. Environment Setup

Copy `.env.example` to `.env` and set your local or cloud preferences:

```bash
cp .env.example .env
```

```env
# .env
LLM_PROVIDER=ollama
LLM_MODEL_ANALYSIS=qwen2.5-coder:3b
LLM_MODEL_OPTIMIZATION=qwen2.5-coder:3b
OLLAMA_BASE_URL=http://localhost:11434
```

> [!TIP]
> **Zero Cloud Cost**: Ensure Ollama is running (`ollama serve`) with `ollama pull qwen2.5-coder:3b` for free, 100% offline local execution.

---

## 💻 CLI Commands & Usage

### 🔍 1. Fast Code Bloat Analysis (`codeslim analyze`)
Scan Python source files or entire directories for complexity, bloat score, and dead imports **without making any LLM calls**:

```bash
codeslim analyze ./codeslim/ --format rich
```

### ⚡ 2. Full Optimization Pipeline (`codeslim optimize`)
Run deterministic CST dead-code removal combined with guarded LLM refactoring:

```bash
codeslim optimize ./target_file.py --apply --backup
```

### 🔭 3. Project Observatory HTML Export (`codeslim scan`)
Scan an entire project directory and export a standalone, interactive Tokyo Night HTML Observatory report:

```bash
codeslim scan ./codeslim/ --export-html observatory_report.html
```

### 🎨 4. Launch Web Studio (`codeslim ui`)
Launch the interactive Tokyo Night Web Studio workspace in your web browser:

```bash
codeslim ui --port 8000
```

### 🤖 5. Start GitHub PR Webhook Bot (`codeslim bot serve`)
Start the FastAPI webhook receiver server for automated Pull Request security and quality audits:

```bash
codeslim bot serve --port 8000 --auto-commit
```

### 🪝 6. Install Pre-Commit Guardrail Hook (`codeslim install-hooks`)
Install the local Git pre-commit hook into `.git/hooks/pre-commit` to automatically strip unused imports before committing:

```bash
codeslim install-hooks
```

---

## 🎯 3-Tier Confidence Classifier

To eliminate breaking changes, CodeSlim categorizes every proposed refactoring action:

```text
┌─────────────────┬───────────────────────────────┬───────────────────────────────┐
│ Tier            │ Action Type                   │ Applied Automatically?        │
├─────────────────┼───────────────────────────────┼───────────────────────────────┤
│ 🟢 Auto-Safe    │ Unused imports & dead code    │ Yes (Deterministic CST Fix)   │
│ 🟡 Suggest      │ Nesting & guard clause logic  │ Subject to AST Safety Gate    │
│ 🔴 Flag-Only    │ Public API signature changes  │ Requires Manual Review        │
└─────────────────┴───────────────────────────────┴───────────────────────────────┘
```

---

## 🧪 Testing & Quality Verification

CodeSlim enforces strict code quality and maintains a **100% green test suite** with 0 linter errors:

```bash
# Run Unit & Integration Tests (96/96 Passing)
python -m pytest -v

# Run Ruff Static Analysis Linter
python -m ruff check codeslim/ tests/

# Run Strict Mypy Type Checker
python -m mypy codeslim/
```

```text
======================== 96 passed, 1 warning in 3.04s ========================
```

---

## 📁 Repository Structure

```text
CodeSlim/
├── codeslim/                    # Core Python Package
│   ├── analyzers/               # Radon, Vulture, Lizard & Tree-Sitter Sensors
│   ├── context/                 # LibCST Minimizer & Docstring Compressor
│   ├── llm/                     # Ollama / OpenAI Dual Provider Engine
│   ├── optimizer/               # AST Safety Gate, Confidence Classifier & Diffs
│   ├── pipeline/                # LangGraph-style Node Orchestration
│   ├── formatters/              # Rich Terminal, JSON, & HTML Observatory Exporters
│   ├── bot/                     # FastAPI GitHub PR Webhook Receiver & Bot
│   └── ui/                      # Tokyo Night Web Studio Server & Web Assets
├── tests/                       # 96 Comprehensive Unit & Integration Tests
├── pyproject.toml               # Package Dependencies & Tool Configurations
├── .env.example                 # Sanitized Environment Configuration Template
└── README.md                    # Project Documentation
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
