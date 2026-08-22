"""Package import verification cache."""

from typing import Any


class VerificationCache:
    """In-memory cache for verified package import results."""

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def get(self, package_name: str) -> Any | None:
        """Get cached result for a package name."""
        return self._cache.get(package_name)

    def set(self, package_name: str, result: Any) -> None:
        """Store verification result for a package name."""
        self._cache[package_name] = result

    def clear(self) -> None:
        """Clear cache entries."""
        self._cache.clear()
