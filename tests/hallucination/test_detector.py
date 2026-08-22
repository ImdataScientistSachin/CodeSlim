"""Unit tests for HallucinationDetector and PyPIVerifier."""

from codeslim.hallucination.detector import HallucinationDetector
from codeslim.hallucination.pypi_verifier import PyPIVerifier


def test_pypi_verifier_known_hallucination():
    """Verify detection of known hallucinated packages."""
    verifier = PyPIVerifier()
    is_fake, msg = verifier.is_known_hallucination("pd_utils")
    assert is_fake is True
    assert "pandas" in msg.lower()

    is_fake_real, _ = verifier.is_known_hallucination("pandas")
    assert is_fake_real is False


def test_hallucination_detector_stdlib_and_fake_imports():
    """Verify import verification categorizes stdlib vs known fake imports."""
    detector = HallucinationDetector()
    imports = [
        {"package_to_verify": "os", "line": 1, "statement": "import os"},
        {"package_to_verify": "pd_utils", "line": 2, "statement": "import pd_utils"},
        {"package_to_verify": "json", "line": 3, "statement": "import json"},
    ]

    report = detector.verify_imports("test_file.py", imports)
    assert report.total_imports_checked == 3
    assert report.has_hallucinations is True
    assert report.hallucinated_count == 1
    assert report.verified_count == 2

    fake_finding = [f for f in report.findings if f.is_hallucinated][0]
    assert fake_finding.package_name == "pd_utils"
    assert fake_finding.verification_source == "depscope"
