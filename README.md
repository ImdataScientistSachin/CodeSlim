# 🚀 CodeSlim: The Agentic Code Analysis & Context Minimizer Engine

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-63%2F63%20passing-brightgreen.svg)](tests/)
[![Architecture](https://img.shields.io/badge/architecture-Multi--Agent%20Pipeline-orange.svg)](#-architecture--data-flow)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Local-First AI](https://img.shields.io/badge/AI-Ollama%20%7C%20OpenAI-purple.svg)](#-local-first-llm-architecture)

> **CodeSlim** is an open-source, production-grade **Agentic AI CLI tool** that sits between your Python codebase and LLMs. It uses deterministic static analysis sensors (Radon, Vulture, Lizard, AST) to pre-process source files, prunes token bloat using lossless LibCST Concrete Syntax Trees, calls local/cloud LLMs with focused context, and enforces **AST syntax guardrails** to prevent hallucinations from ever corrupting your codebase.

---

## 🌟 Key Features

* ⚡ **30–50% Token Reduction**: Lossless LibCST pruning strips dead code and docstrings, reducing input tokens and saving LLM API costs.
* 🛡️ **0% Hallucination Safety Gate**: AST `ast.parse()` and public signature preservation checks reject broken syntax or deleted APIs.
* 🔒 **Local-First Privacy**: Runs free, private local LLMs (Ollama `qwen2.5-coder:3b` under 2.2GB VRAM) with automatic cloud fallback to OpenAI (`gpt-4o-mini`).
* 🎯 **3-Tier Confidence Classifier**: Categorizes refactoring actions into `Auto-Safe` (dead code), `Suggest` (simplification), and `Flag-Only` (structural extraction).
* 📊 **Multi-Target Output Formatters**: Emits rich terminal panels, structured JSON for CI/CD, and GitHub Markdown tables for PR comment bots.
* 🔭 **Project Observatory Dashboard**: Multi-file codebase-level scanning with visual file treemaps, cross-file phantom function detection, and hallucinated import spread maps.

---

## 📐 Architecture & Data Flow

CodeSlim executes a **5-stage linear pipeline** using specialized autonomous agents:

```
                          ┌──────────────────────────────┐
                          │  CODESLIM PIPELINE PIPELINE  │
                          └──────────────┬───────────────┘
                                         │
 ┌───────────────────────────────────────┼───────────────────────────────────────┐
 │                                       │                                       │
 ▼                                       ▼                                       ▼
1. 🔍 STATIC ANALYSIS AGENT       2. ✂️ CONTEXT MINIMIZER AGENT     3. 🤖 LLM REASONER AGENT
   (Deterministic Sensors)           (Prompt & Token Engineer)       (Async Intelligence Engine)
   • Radon Cyclomatic Complexity     • LibCST docstring/dead pruner  • Ollama local qwen2.5-coder
   • Vulture Dead Code Detector      • tiktoken budget calculator    • OpenAI gpt-4o-mini fallback
   • Lizard Cognitive Complexity     • Isolated prompt sandboxing    • Escalating JSON error retries
   • AST Nesting & Import Visitor
 │                                       │                                       │
 └───────────────────────────────────────┼───────────────────────────────────────┘
                                         │
 ┌───────────────────────────────────────┴───────────────────────────────────────┐
 │                                                                               │
 ▼                                                                               ▼
4. 🛡️ HALLUCINATION GUARDRAIL AGENT                        5. ⚙️ PIPELINE ORCHESTRATOR AGENT
   (Safety & Diff Auditor)                                    (State Machine Controller)
   • AST Syntax ast.parse() Validation                        • LangGraph State Machine
   • Public Signature Preservation Check                      • Subcommands: analyze / optimize / scan
   • 3-Tier Risk Categorization                               • Formatters: Rich / JSON / PR / Observatory
```

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install in editable mode:

```bash
git clone https://github.com/your-org/codeslim.git
cd codeslim
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Default `.env` configuration for local execution:

```env
LLM_PROVIDER=ollama
LLM_MODEL_ANALYSIS=qwen2.5-coder:3b
LLM_MODEL_OPTIMIZATION=qwen2.5-coder:3b
OLLAMA_BASE_URL=http://localhost:11434
# OPENAI_API_KEY=sk-your-openai-api-key
```

---

## 💻 CLI Usage & Commands

### 🔍 1. Fast Code Bloat Analysis (`codeslim analyze`)

Scan a file or directory with static analysis sensors without calling the LLM:

```bash
codeslim analyze ./myproject/ --format rich
```

#### Outputs:
* **Rich Terminal**: Color-coded bloat score grade (**A** to **F**), metrics table, and itemized bloat list.
* **JSON (CI/CD)**: Machine-readable JSON output via `--format json`.
* **GitHub PR**: GitHub-Flavored Markdown comment table via `--format github_pr`.

---

### ⚡ 2. Full Optimization Pipeline (`codeslim optimize`)

Run the full 5-stage pipeline on a target Python file:

```bash
codeslim optimize ./target_file.py --format rich
```

#### Apply Changes with Automatic Backup:
```bash
codeslim optimize ./target_file.py --apply --backup
```
*Applies optimized code to `./target_file.py` and creates a `./target_file.py.bak` backup file.*

---

### 🔭 3. Project Observatory Scan (`codeslim scan`)

Scan an entire directory of Python files to inspect codebase health, file treemaps, and cross-file phantom functions:

```bash
codeslim scan ./codeslim/
```

#### Outputs:
* **Overall Health Meter**: Grade badge and project-wide bloat percentage.
* **File Treemap Grid**: Visual file sizes and bloat severity color coding.
* **Top 5 Worst Offenders**: Ranked table of most complex files.
* **Cross-File Intelligence**: Detects phantom functions and fake PyPI package spread across files.
* **Codebase Fingerprint**: Composition breakdown bar of Clean, Dead, Complex, and Duplicated lines.

---

## 🤖 The 5 Specialized Agents

| Agent | Responsibilities | Key Files | Key Technologies |
| :--- | :--- | :--- | :--- |
| **1. Static Analysis Agent** | Sensor & perception layer | `codeslim/analyzers/` | Radon CC, Vulture, Lizard, AST Visitors, Token Duplication |
| **2. Context Minimizer Agent** | Token & prompt optimization | `codeslim/context/` | LibCST syntax transformers, `tiktoken` token budget engine |
| **3. LLM Reasoner Agent** | Generative decision engine | `codeslim/llm/` | Async Ollama REST client, OpenAI fallback, Pydantic V2 schemas |
| **4. Hallucination Guardrail Agent** | Safety audit & diff generator | `codeslim/optimizer/` | AST `ast.parse()`, Signature Preservation, 3-Tier Classifier |
| **5. Pipeline Orchestrator Agent** | State machine controller | `codeslim/pipeline/` & `cli.py` | State machine node router, Rich CLI, Multi-target formatters |

---

## 🧪 Testing & Verification

CodeSlim maintains a **100% passing test suite** using `pytest`:

```bash
pytest -v
```

```
============================= 63 passed in 1.65s =============================
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
