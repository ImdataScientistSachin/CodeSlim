"""Unit tests for NPMVerifier."""

from codeslim.hallucination.npm_verifier import NPMVerifier


class TestNPMVerifier:
    """Validate NPM offline hallucination verification."""

    def test_known_npm_hallucination_detected(self) -> None:
        verifier = NPMVerifier()
        is_fake, msg = verifier.is_known_hallucination("react-utils-core")
        assert is_fake is True
        assert "React" in msg

    def test_valid_npm_package_not_flagged(self) -> None:
        verifier = NPMVerifier()
        is_fake, msg = verifier.is_known_hallucination("express")
        assert is_fake is False
        assert msg == ""
