"""AST Invariant Safety Gate for CodeSlim Node 5.

Verifies that LLM-refactored code preserves all public signatures,
decorator list invariants, and async coroutine declarations.
"""

import ast
from typing import Any


class ASTInvariantGate:
    """AST Safety Gate enforcing strict interface and signature preservation."""

    def extract_signatures(self, code: str) -> dict[str, dict[str, Any]]:
        """Extract public functions, classes, decorators, and coroutine statuses.

        Args:
            code: The Python source string.

        Returns:
            A dictionary mapping symbol names to their AST metadata.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {}

        symbols: dict[str, dict[str, Any]] = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = [ast.unparse(d).strip() for d in node.decorator_list]
                args = [arg.arg for arg in node.args.args]
                symbols[node.name] = {
                    "type": "function",
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "decorators": sorted(decorators),
                    "args": args,
                }
            elif isinstance(node, ast.ClassDef):
                decorators = [ast.unparse(d).strip() for d in node.decorator_list]
                symbols[node.name] = {
                    "type": "class",
                    "decorators": sorted(decorators),
                }

        return symbols

    def is_safe(self, original_code: str, refactored_code: str) -> bool:
        """Verify that refactored code preserves all public AST invariants of original code.

        Args:
            original_code: Original source code.
            refactored_code: Refactored source code.

        Returns:
            True if all AST invariants are preserved, False if mutated/broken.
        """
        orig_symbols = self.extract_signatures(original_code)
        ref_symbols = self.extract_signatures(refactored_code)

        if not orig_symbols:
            return True

        for name, orig_meta in orig_symbols.items():
            # Private symbols (starting with _) can be refactored internally
            if name.startswith("_"):
                continue

            if name not in ref_symbols:
                return False

            ref_meta = ref_symbols[name]

            # Type check
            if orig_meta["type"] != ref_meta["type"]:
                return False

            # Async coroutine status check
            if orig_meta.get("is_async") != ref_meta.get("is_async"):
                return False

            # Decorator list invariance check (@staticmethod, @property, etc.)
            if orig_meta["decorators"] != ref_meta["decorators"]:
                return False

            # Argument signature check
            if "args" in orig_meta and orig_meta["args"] != ref_meta.get("args"):
                return False

        return True
