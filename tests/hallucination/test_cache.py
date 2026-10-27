"""Unit tests for VerificationCache."""

from codeslim.hallucination.cache import VerificationCache


def test_verification_cache() -> None:
    cache = VerificationCache()
    assert cache.get("numpy") is None

    cache.set("numpy", {"valid": True})
    assert cache.get("numpy") == {"valid": True}

    cache.clear()
    assert cache.get("numpy") is None
