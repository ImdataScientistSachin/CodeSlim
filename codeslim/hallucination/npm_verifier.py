"""npm package registry verifier."""

KNOWN_NPM_HALLUCINATIONS = {
    "react-utils-core": "Non-existent React utility package.",
    "express-helpers-v2": "Non-existent Express helper package.",
}


class NPMVerifier:
    """Verifies Node.js/npm package import statements."""

    def __init__(self) -> None:
        self.known_hallucinations = KNOWN_NPM_HALLUCINATIONS

    def is_known_hallucination(self, package_name: str) -> tuple[bool, str]:
        """Check if npm package is a known LLM hallucination."""
        if package_name in self.known_hallucinations:
            return True, self.known_hallucinations[package_name]
        return False, ""
