"""
LibCST Code Pruner Module for CodeSlim.

Applies lossless Concrete Syntax Tree (CST) transformations to Python source code:
- Removes dead code statements identified by Vulture static analysis.
- Strips unused import statements deterministically.
- Strips module-level and function-level docstrings safely.
- Inserts `pass` statements if stripping empties a block body.
"""

from collections.abc import Sequence

import libcst as cst
from libcst.metadata import CodeRange, MetadataWrapper, PositionProvider

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.context.pruner")


class RemoveUnusedImportsTransformer(cst.CSTTransformer):
    """
    LibCST transformer that removes import statements flagged as unused
    by Vulture static analysis.
    """

    def __init__(self, unused_names: set[str]) -> None:
        super().__init__()
        self.unused_names = unused_names

    def _get_name_str(self, node: cst.CSTNode) -> str:
        if isinstance(node, cst.Name):
            return node.value
        if isinstance(node, cst.Attribute):
            return node.attr.value
        return str(node)

    def leave_Import(
        self,
        original_node: cst.Import,
        updated_node: cst.Import,
    ) -> cst.Import | cst.RemovalSentinel:
        names: Sequence[cst.ImportAlias] = updated_node.names
        kept = []
        for alias in names:
            name_val = self._get_name_str(alias.name)
            asname_val = self._get_name_str(alias.asname.name) if alias.asname else None
            if name_val not in self.unused_names and (asname_val is None or asname_val not in self.unused_names):
                kept.append(alias)

        if not kept:
            return cst.RemoveFromParent()
        if len(kept) < len(names):
            return updated_node.with_changes(names=kept)
        return updated_node

    def leave_ImportFrom(
        self,
        original_node: cst.ImportFrom,
        updated_node: cst.ImportFrom,
    ) -> cst.ImportFrom | cst.RemovalSentinel:
        if isinstance(updated_node.names, cst.ImportStar):
            return updated_node

        names: Sequence[cst.ImportAlias] = updated_node.names
        kept = []
        for alias in names:
            name_val = self._get_name_str(alias.name)
            if name_val not in self.unused_names:
                kept.append(alias)

        if not kept:
            return cst.RemoveFromParent()
        if len(kept) < len(names):
            return updated_node.with_changes(names=kept)
        return updated_node


class DocstringAndDeadCodeTransformer(cst.CSTTransformer):
    """
    CST Transformer to strip dead code statements and docstrings.
    """

    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, dead_code_lines: set[int], strip_docstrings: bool = True) -> None:
        super().__init__()
        self.dead_code_lines = dead_code_lines
        self.strip_docstrings = strip_docstrings

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine | cst.RemovalSentinel:
        pos: CodeRange = self.get_metadata(PositionProvider, original_node)
        start_line = pos.start.line
        end_line = pos.end.line

        if any(line in self.dead_code_lines for line in range(start_line, end_line + 1)):
            log.debug("pruning_dead_code_line", start=start_line, end=end_line)
            return cst.RemoveFromParent()

        if self.strip_docstrings and self._is_docstring_statement(original_node):
            log.debug("pruning_docstring", start=start_line, end=end_line)
            return cst.RemoveFromParent()

        return updated_node

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef) -> cst.FunctionDef:
        if not updated_node.body.body:
            pass_stmt = cst.SimpleStatementLine(body=[cst.Pass()])
            log.debug("inserting_pass_statement", function=updated_node.name.value)
            return updated_node.with_changes(body=cst.IndentedBlock(body=[pass_stmt]))
        return updated_node

    def _is_docstring_statement(self, node: cst.SimpleStatementLine) -> bool:
        if len(node.body) == 1 and isinstance(node.body[0], cst.Expr):
            expr_value = node.body[0].value
            if isinstance(expr_value, (cst.SimpleString, cst.FormattedString, cst.ConcatenatedString)):
                return True
        return False


def remove_unused_imports(code: str, unused_names: set[str]) -> str:
    """
    Remove unused import statements from Python source code using LibCST.

    Args:
        code: Target Python source code string.
        unused_names: Set of symbol names flagged as unused.

    Returns:
        Cleaned source code string.
    """
    if not code.strip() or not unused_names:
        return code
    try:
        module = cst.parse_module(code)
        transformer = RemoveUnusedImportsTransformer(unused_names=unused_names)
        return module.visit(transformer).code
    except Exception as exc:
        log.warning("import_removal_failed", error=str(exc))
        return code


def prune_source_code(
    raw_code: str,
    dead_code_lines: set[int] | None = None,
    strip_docstrings: bool = True,
) -> str:
    """
    Prune docstrings and dead code lines from Python source code string.

    Args:
        raw_code: Input Python source code string.
        dead_code_lines: Set of 1-based line numbers containing dead code.
        strip_docstrings: Whether to remove docstring statements.

    Returns:
        Pruned source code string.
    """
    if not raw_code.strip():
        return raw_code

    dead_lines = dead_code_lines or set()

    try:
        module = cst.parse_module(raw_code)
        wrapper = MetadataWrapper(module)
        transformer = DocstringAndDeadCodeTransformer(
            dead_code_lines=dead_lines,
            strip_docstrings=strip_docstrings,
        )
        modified_module = wrapper.visit(transformer)
        return modified_module.code
    except Exception as exc:
        log.warning("libcst_pruning_failed_returning_raw", error=str(exc))
        return raw_code
