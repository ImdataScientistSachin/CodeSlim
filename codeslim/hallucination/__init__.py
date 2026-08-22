"""
Hallucination Detection & Verification Package for CodeSlim.

Provides package import verification against standard library modules,
local virtual environment specifications, and known LLM hallucination datasets.
"""

from codeslim.hallucination.detector import HallucinationDetector
from codeslim.hallucination.pypi_verifier import PyPIVerifier

__all__ = ["HallucinationDetector", "PyPIVerifier"]
