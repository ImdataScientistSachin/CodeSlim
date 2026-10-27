"""Unit tests for PyPIVerifier and DepScope integration."""

from codeslim.hallucination.depscope_client import DepScopeClient
from codeslim.hallucination.pypi_verifier import PyPIVerifier


class TestPyPIVerifier:
    """Validate PyPI offline hallucination verification."""

    def test_known_hallucination_detected(self) -> None:
        verifier = PyPIVerifier()
        is_fake, msg = verifier.is_known_hallucination("pd_utils")
        assert is_fake is True
        assert "pandas" in msg

    def test_valid_package_not_flagged(self) -> None:
        verifier = PyPIVerifier()
        is_fake, msg = verifier.is_known_hallucination("numpy")
        assert is_fake is False
        assert msg == ""

    def test_external_dataset_sync(self) -> None:
        client = DepScopeClient()
        is_fake, desc = client.is_hallucinated("torch_helpers")
        assert is_fake is True
        assert "PyTorch" in desc
