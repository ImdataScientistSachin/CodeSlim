"""Static Analyzers package for CodeSlim."""

from codeslim.analyzers.ast_analyzer import ASTAnalyzer
from codeslim.analyzers.base import BaseAnalyzer
from codeslim.analyzers.cognitive import CognitiveAnalyzer
from codeslim.analyzers.complexity import ComplexityAnalyzer
from codeslim.analyzers.dead_code import DeadCodeAnalyzer
from codeslim.analyzers.duplication import DuplicationAnalyzer

__all__ = [
    "BaseAnalyzer",
    "ComplexityAnalyzer",
    "DeadCodeAnalyzer",
    "ASTAnalyzer",
    "CognitiveAnalyzer",
    "DuplicationAnalyzer",
]
