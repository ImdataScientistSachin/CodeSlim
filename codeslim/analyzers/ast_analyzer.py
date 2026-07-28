"""
AST Analyzer Module for CodeSlim.

Parses Python Abstract Syntax Trees to extract:
- Control flow nesting depth.
- Import statements categorized into stdlib, third-party, and relative/local imports.
- Codebase context (top-level functions, classes, and imports) for multi-file analysis.
"""

import ast
import sys
from pathlib import Path
from typing import Any

from codeslim.analyzers.base import BaseAnalyzer
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.analyzers.ast_analyzer")

# Standard library module set for fast import categorization
STDLIB_MODULES = (
    set(sys.stdlib_module_names)
    if hasattr(sys, "stdlib_module_names")
    else {
        "os",
        "sys",
        "json",
        "time",
        "datetime",
        "math",
        "random",
        "re",
        "pathlib",
        "typing",
        "collections",
        "functools",
        "itertools",
        "ast",
        "hashlib",
        "sqlite3",
        "unittest",
        "abc",
        "inspect",
        "io",
        "copy",
        "logging",
        "asyncio",
        "threading",
    }
)


class NestingVisitor(ast.NodeVisitor):
    """AST visitor to compute maximum block nesting depth."""

    def __init__(self) -> None:
        self.current_depth = 0
        self.max_depth = 0

    def _visit_block(self, node: ast.AST) -> None:
        self.current_depth += 1
        if self.current_depth > self.max_depth:
            self.max_depth = self.current_depth
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_If(self, node: ast.If) -> None:
        self._visit_block(node)

    def visit_For(self, node: ast.For) -> None:
        self._visit_block(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._visit_block(node)

    def visit_While(self, node: ast.While) -> None:
        self._visit_block(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._visit_block(node)

    def visit_With(self, node: ast.With) -> None:
        self._visit_block(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self._visit_block(node)


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract and categorize import statements."""

    def __init__(self) -> None:
        self.imports: list[dict[str, Any]] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            top_level = alias.name.split(".")[0]
            self.imports.append(
                {
                    "module": alias.name,
                    "package_to_verify": top_level,
                    "statement": f"import {alias.name}",
                    "line": node.lineno,
                    "is_relative": False,
                    "level": 0,
                }
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        # Check node.level to strictly identify relative imports
        is_relative = node.level > 0 if node.level is not None else False
        module_name = node.module if node.module else ""
        package_to_verify = "" if is_relative else (module_name.split(".")[0] if module_name else "")

        for alias in node.names:
            dots = "." * (node.level or 0)
            stmt = f"from {dots}{module_name} import {alias.name}"
            self.imports.append(
                {
                    "module": module_name,
                    "imported_name": alias.name,
                    "package_to_verify": package_to_verify,
                    "statement": stmt,
                    "line": node.lineno,
                    "is_relative": is_relative,
                    "level": node.level or 0,
                }
            )


class ASTAnalyzer(BaseAnalyzer):
    """Analyzes Python source files via standard library AST."""

    def name(self) -> str:
        return "ast_analyzer"

    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Extract AST metrics from a Python source file.

        Args:
            file_path: Path to target file.

        Returns:
            Dict containing nesting depth, import lists, and categorization.
        """
        if not file_path.exists():
            log.error("file_not_found", path=str(file_path))
            raise FileNotFoundError(f"Source file not found: {file_path}")

        code = file_path.read_text(encoding="utf-8")
        if not code.strip():
            return {
                "max_nesting_depth": 0,
                "all_imports": [],
                "third_party_imports": [],
                "stdlib_imports": [],
                "relative_imports": [],
            }

        try:
            tree = ast.parse(code, filename=file_path.name)
        except SyntaxError as exc:
            log.warning("syntax_error_in_ast", file=file_path.name, line=exc.lineno, msg=exc.msg)
            return {
                "max_nesting_depth": 0,
                "all_imports": [],
                "third_party_imports": [],
                "stdlib_imports": [],
                "relative_imports": [],
                "syntax_error": str(exc),
            }

        nesting_visitor = NestingVisitor()
        nesting_visitor.visit(tree)

        import_visitor = ImportVisitor()
        import_visitor.visit(tree)

        third_party: set[str] = set()
        stdlib: set[str] = set()
        relative: list[dict[str, Any]] = []

        for imp in import_visitor.imports:
            if imp["is_relative"]:
                relative.append(imp)
            else:
                pkg = imp["package_to_verify"]
                if pkg:
                    if pkg in STDLIB_MODULES:
                        stdlib.add(pkg)
                    else:
                        third_party.add(pkg)

        log.info(
            "ast_analysis_complete",
            file=file_path.name,
            max_nesting_depth=nesting_visitor.max_depth,
            total_imports=len(import_visitor.imports),
            third_party_count=len(third_party),
            relative_count=len(relative),
        )

        return {
            "max_nesting_depth": nesting_visitor.max_depth,
            "all_imports": import_visitor.imports,
            "third_party_imports": sorted(list(third_party)),
            "stdlib_imports": sorted(list(stdlib)),
            "relative_imports": relative,
        }

    def extract_local_context(self, file_path: Path) -> dict[str, Any]:
        """
        Extract top-level functions, classes, and imports for local context.

        Args:
            file_path: Path to target file.

        Returns:
            Dict containing top-level function names, class names, and import statements.
        """
        if not file_path.exists():
            return {"top_level_functions": [], "classes": [], "imports": []}

        try:
            tree = ast.parse(file_path.read_text(encoding="utf-8"))
        except Exception:
            return {"top_level_functions": [], "classes": [], "imports": []}

        functions: list[str] = []
        classes: list[str] = []

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

        import_visitor = ImportVisitor()
        import_visitor.visit(tree)
        imports = [imp["statement"] for imp in import_visitor.imports]

        return {
            "top_level_functions": functions,
            "classes": classes,
            "imports": imports,
        }
