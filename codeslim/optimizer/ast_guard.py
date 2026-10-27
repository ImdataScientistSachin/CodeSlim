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

    def validate(self, original_code: str, refactored_code: str) -> tuple[bool, list[str]]:
        """Verify AST invariants and return safety status with specific error traces.

        Args:
            original_code: Original source code.
            refactored_code: Refactored source code.

        Returns:
            Tuple of (is_safe: bool, violations: list[str]).
        """
        try:
            ast.parse(original_code)
        except SyntaxError:
            # If original code is malformed, cannot enforce diff invariants
            return True, []

        try:
            ast.parse(refactored_code)
        except SyntaxError as exc:
            return False, [f"SyntaxError in refactored code: {exc.msg} at line {exc.lineno}"]

        orig_symbols = self.extract_signatures(original_code)
        ref_symbols = self.extract_signatures(refactored_code)

        if not orig_symbols:
            return True, []

        violations: list[str] = []

        for name, orig_meta in orig_symbols.items():
            # Private symbols (starting with _) can be refactored internally
            if name.startswith("_"):
                continue

            if name not in ref_symbols:
                violations.append(f"Missing public symbol: '{name}' was deleted or renamed in refactored code.")
                continue

            ref_meta = ref_symbols[name]

            # Type check
            if orig_meta["type"] != ref_meta["type"]:
                violations.append(
                    f"Type mutation for '{name}': changed from {orig_meta['type']} to {ref_meta['type']}."
                )

            # Async coroutine status check
            if orig_meta.get("is_async") != ref_meta.get("is_async"):
                orig_async = "async def" if orig_meta.get("is_async") else "def"
                ref_async = "async def" if ref_meta.get("is_async") else "def"
                violations.append(
                    f"Async declaration altered for '{name}': expected '{orig_async}', got '{ref_async}'."
                )

            # Decorator list invariance check (@staticmethod, @property, etc.)
            if orig_meta["decorators"] != ref_meta["decorators"]:
                violations.append(
                    f"Decorators mutated for '{name}': expected {orig_meta['decorators']}, got {ref_meta['decorators']}."
                )

            # Argument signature check
            if "args" in orig_meta and orig_meta["args"] != ref_meta.get("args"):
                violations.append(
                    f"Signature arguments mutated for '{name}': expected {orig_meta['args']}, got {ref_meta.get('args')}."
                )

        return len(violations) == 0, violations

    def is_safe(self, original_code: str, refactored_code: str) -> bool:
        """Verify that refactored code preserves all public AST invariants of original code.

        Args:
            original_code: Original source code.
            refactored_code: Refactored source code.

        Returns:
            True if all AST invariants are preserved, False if mutated/broken.
        """
        is_valid, _ = self.validate(original_code, refactored_code)
        return is_valid

