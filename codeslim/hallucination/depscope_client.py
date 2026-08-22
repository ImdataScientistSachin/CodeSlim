"""DepScope dataset client for hallucination verification."""

import json
from pathlib import Path


class DepScopeClient:
    """Client for querying the DepScope fake package dataset."""

    def __init__(self) -> None:
        self.dataset_path = Path(__file__).parent / "known_hallucinations.json"
        self._dataset: dict[str, str] = self._load_dataset()

    def _load_dataset(self) -> dict[str, str]:
        """Load known hallucinated package dataset from disk."""
        if not self.dataset_path.exists():
            return {}
        try:
            return json.loads(self.dataset_path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def is_hallucinated(self, package_name: str) -> tuple[bool, str]:
        """Check if package is listed in DepScope dataset."""
        if package_name in self._dataset:
            return True, self._dataset[package_name]
        return False, ""
