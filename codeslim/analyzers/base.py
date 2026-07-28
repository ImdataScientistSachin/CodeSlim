"""
Base Analyzer Interface for CodeSlim.

Defines the abstract contract that all static code analyzers implement,
enabling uniform orchestration by the LangGraph pipeline.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseAnalyzer(ABC):
    """Abstract base for all CodeSlim static analyzers."""

    @abstractmethod
    def name(self) -> str:
        """Return a unique identifier for this analyzer."""

    @abstractmethod
    def analyze(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a Python source file and return structured results.

        Args:
            file_path: Path to the target .py file.

        Returns:
            Dictionary of normalized metrics or findings.

        Raises:
            FileNotFoundError: If target file does not exist.
        """
