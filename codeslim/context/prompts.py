"""
System and User Prompt Templates for CodeSlim Context Engine.

Enforces strict separation of system instructions and user source code
to prevent prompt duplication and token overhead.
"""

SYSTEM_ANALYSIS_PROMPT = """You are CodeSlim's Agentic Refactoring Engine.
Your task is to analyze Python source code and static analysis metrics to propose structured refactoring actions.

Strict Guidelines:
1. SIGNATURE PRESERVATION MANDATE: You MUST retain every top-level class definition (`class X:`) and function definition (`def y():`). Do NOT omit any class or function headers.
2. Preserve all public function signatures, parameter names, and return types.
3. Output ONLY valid JSON matching the refactoring response schema.
4. Do NOT invent or import non-existent packages or hallucinated APIs.
5. Focus on reducing cyclomatic complexity, flattening nested conditionals, and removing dead code.
"""

USER_ANALYSIS_PROMPT_TEMPLATE = """[Target Analysis Data]
File: {file_name}
Bloat Score: {bloat_score:.2f}
Max Cyclomatic Complexity: {max_cc}
Dead Code Count: {dead_code_count}

[Pruned Python Source Code]
```python
{pruned_code}
```

[REQUIRED OUTPUT FORMAT — Respond with ONLY this JSON object structure, no other text]
{{
  "summary": "Brief explanation of refactoring changes made",
  "actions": [
    {{
      "action_type": "simplify_complexity",
      "target_symbol": "function_name_here",
      "line_start": 1,
      "line_end": 30,
      "explanation": "Why this change was made"
    }}
  ],
  "optimized_code": "# Complete refactored Python source code here",
  "confidence_score": 0.85
}}
"""


def build_user_prompt(
    file_name: str,
    bloat_score: float,
    max_cc: int,
    dead_code_count: int,
    pruned_code: str,
) -> str:
    """Format user prompt without duplicating system instructions."""
    return USER_ANALYSIS_PROMPT_TEMPLATE.format(
        file_name=file_name,
        bloat_score=bloat_score,
        max_cc=max_cc,
        dead_code_count=dead_code_count,
        pruned_code=pruned_code.strip(),
    )
