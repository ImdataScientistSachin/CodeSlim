"""
GBNF (GGML BNF) Grammar Templates for CodeSlim Local LLM Constrained Decoding.

Provides formal context-free grammars used by llama.cpp and Ollama (`grammar` parameter)
to guarantee logit-level schema adherence, eliminating JSON decode errors and enforcing
valid Python function structures when running ultra-compact models like qwen2.5-coder:1.5b.
"""

from __future__ import annotations

# GBNF grammar strictly enforcing valid JSON matching LLMRefactorResponse schema
GBNF_JSON_REFACTOR = r"""root ::= "{" ws "\"summary\":" ws string "," ws "\"actions\":" ws actions_list "," ws "\"optimized_code\":" ws string "," ws "\"confidence_score\":" ws number ws "}"
actions_list ::= "[" ws (action ("," ws action)*)? ws "]"
action ::= "{" ws "\"action_type\":" ws string "," ws "\"target_symbol\":" ws string "," ws "\"line_start\":" ws integer "," ws "\"line_end\":" ws integer "," ws "\"explanation\":" ws string ws "}"
string ::= "\"" ([^"\\] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""
number ::= ("-"? [0-9]+ ("." [0-9]+)?)
integer ::= ("-"? [0-9]+)
ws ::= [ \t\n\r]*
"""

# GBNF grammar enforcing valid Python function syntax for chunked refactoring
GBNF_PYTHON_FUNCTION = r"""root ::= (decorator ws)* function_def
decorator ::= "@" [a-zA-Z_] [a-zA-Z0-9_.]* ("(" [^)]* ")")? ws
function_def ::= ("async " ws)? "def " identifier "(" params? ")" (" -> " return_type)? ":" ws body
params ::= [^)]+
return_type ::= [^:]+
body ::= statement+
statement ::= ws [^\n]+ "\n"
identifier ::= [a-zA-Z_] [a-zA-Z0-9_]*
ws ::= [ \t]*
"""

GBNF_TEMPLATES: dict[str, str] = {
    "json_refactor": GBNF_JSON_REFACTOR,
    "python_function": GBNF_PYTHON_FUNCTION,
}


def get_grammar_template(name: str) -> str | None:
    """
    Retrieve a pre-compiled GBNF grammar template by identifier.

    Args:
        name: Name of template ('json_refactor' or 'python_function').

    Returns:
        GBNF grammar string if registered, otherwise None.
    """
    return GBNF_TEMPLATES.get(name)
