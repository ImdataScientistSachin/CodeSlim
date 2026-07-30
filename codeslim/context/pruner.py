
from collections.abc import Sequence

import libcst as cst
from libcst.metadata import CodeRange, MetadataWrapper, PositionProvider

from codeslim.utils.logger import get_logger

log = get_logger("codeslim.context.pruner")


class RemoveUnusedImportsTransformer(cst.CSTTransformer):

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
            last_alias = kept[-1]
            if last_alias.comma != cst.MaybeSentinel.DEFAULT:
                kept[-1] = last_alias.with_changes(comma=cst.MaybeSentinel.DEFAULT)
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
            if not getattr(updated_node, "rpar", None) and not getattr(updated_node, "lpar", None):
                last_alias = kept[-1]
                if last_alias.comma != cst.MaybeSentinel.DEFAULT:
                    kept[-1] = last_alias.with_changes(comma=cst.MaybeSentinel.DEFAULT)
            return updated_node.with_changes(names=kept)
        return updated_node


class DocstringAndDeadCodeTransformer(cst.CSTTransformer):
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
        pos = self.get_metadata(PositionProvider, original_node)
        if not isinstance(pos, CodeRange):
            return updated_node

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


class RemoveDeadFunctionsTransformer(cst.CSTTransformer):

    def __init__(self, dead_function_names: set[str]) -> None:
        super().__init__()
        self.dead_function_names = dead_function_names
        self._class_depth = 0

    def visit_ClassDef(self, node: cst.ClassDef) -> bool:
        self._class_depth += 1
        return True

    def leave_ClassDef(
        self, original_node: cst.ClassDef, updated_node: cst.ClassDef
    ) -> cst.ClassDef:
        self._class_depth -= 1
        return updated_node

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef | cst.RemovalSentinel:
        if self._class_depth > 0:
            return updated_node
        func_name = updated_node.name.value
        if func_name in self.dead_function_names and not func_name.startswith("__"):
            log.debug("pruning_dead_function", function=func_name)
            return cst.RemoveFromParent()
        return updated_node


def prune_source_code(
    code: str,
    dead_code_lines: set[int] | None = None,
    strip_docstrings: bool = True,
) -> str:
    """
    Prune docstrings and dead code lines from Python source code using LibCST.

    Args:
        code: Source code string to prune.
        dead_code_lines: Set of 1-indexed line numbers flagged as dead.
        strip_docstrings: If True, strip docstring statements.

    Returns:
        Pruned source code string.
    """
    if not code.strip():
        return code
    if dead_code_lines is None:
        dead_code_lines = set()
    try:
        wrapper = MetadataWrapper(cst.parse_module(code))
        transformer = DocstringAndDeadCodeTransformer(
            dead_code_lines=dead_code_lines,
            strip_docstrings=strip_docstrings,
        )
        modified_module = wrapper.visit(transformer)
        return modified_module.code
    except Exception as exc:
        err_msg = str(exc).encode("ascii", errors="replace").decode("ascii")
        log.warning("cst_pruning_failed", error=err_msg)
        return code


def remove_dead_functions(code: str, dead_function_names: set[str]) -> str:
    """
    Remove top-level unused function definitions from source code using LibCST.

    Args:
        code: Target Python source code string.
        dead_function_names: Set of top-level function names to remove.

    Returns:
        Source code with unused functions removed.
    """
    if not code.strip() or not dead_function_names:
        return code
    try:
        module = cst.parse_module(code)
        transformer = RemoveDeadFunctionsTransformer(dead_function_names=dead_function_names)
        return module.visit(transformer).code
    except Exception as exc:
        err_msg = str(exc).encode("ascii", errors="replace").decode("ascii")
        log.warning("dead_function_removal_failed", error=err_msg)
        return code


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
        err_msg = str(exc).encode("ascii", errors="replace").decode("ascii")
        log.warning("import_removal_failed", error=err_msg)
        return code



