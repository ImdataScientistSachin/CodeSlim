"""
Unit tests for Python AST Analyzer (ASTAnalyzer).
"""

from pathlib import Path

from codeslim.analyzers.ast_analyzer import ASTAnalyzer


def test_ast_analyzer_nesting_and_imports(tmp_path: Path) -> None:
    code = """
import os
import sys
import httpx
from . import base

def nested_loop():
    if True:
        for i in range(10):
            while False:
                pass
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = ASTAnalyzer()
    res = analyzer.analyze(test_file)

    assert res["max_nesting_depth"] == 3
    assert "os" in res["stdlib_imports"]
    assert "httpx" in res["third_party_imports"]
    assert len(res["relative_imports"]) == 1
    assert res["relative_imports"][0]["is_relative"] is True


def test_ast_analyzer_extract_local_context(tmp_path: Path) -> None:
    code = """
import os

class DataProcessor:
    pass

def process_item():
    pass
"""
    test_file = tmp_path / "sample.py"
    test_file.write_text(code, encoding="utf-8")

    analyzer = ASTAnalyzer()
    context = analyzer.extract_local_context(test_file)

    assert "process_item" in context["top_level_functions"]
    assert "DataProcessor" in context["classes"]
    assert "import os" in context["imports"]
