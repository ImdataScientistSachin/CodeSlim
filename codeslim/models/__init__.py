"""
Data Models module for CodeSlim.

Provides validated Pydantic V2 data structures used across the entire pipeline.
Import models directly from this package for clean access:

    from codeslim.models import FileMetrics, CodeSlimReport, HallucinationFinding
"""

from codeslim.models.hallucination import HallucinationFinding, HallucinationReport
from codeslim.models.metrics import DeadCodeItem, FileMetrics, FunctionMetrics
from codeslim.models.report import BloatMapEntry, CodeSlimReport, ConfidenceTiers

__all__ = [
    "FunctionMetrics",
    "DeadCodeItem",
    "FileMetrics",
    "HallucinationFinding",
    "HallucinationReport",
    "BloatMapEntry",
    "ConfidenceTiers",
    "CodeSlimReport",
]
