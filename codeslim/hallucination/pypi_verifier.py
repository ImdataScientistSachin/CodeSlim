"""PyPI package registry verifier."""


from codeslim.utils.logger import get_logger

log = get_logger("codeslim.hallucination.pypi_verifier")

# Known fake/hallucinated packages for offline deterministic verification
KNOWN_HALLUCINATIONS = {
    "pd_utils": "Non-existent pandas helper package often hallucinated by LLMs. Use pandas directly.",
    "sklearn_extra": "Non-existent scikit-learn helper package. Use sklearn or scikit-learn-extra.",
    "np_helpers": "Non-existent numpy helper package. Use numpy functions directly.",
    "tf_utils": "Non-existent TensorFlow wrapper package. Use tf.keras or tensorflow directly.",
    "torch_helpers": "Non-existent PyTorch utility package. Use torch.nn or torchvision.",
}


class PyPIVerifier:
    """Verifies Python import package validity against stdlib and known package lists."""

    def __init__(self) -> None:
        self.known_hallucinations = KNOWN_HALLUCINATIONS

    def is_known_hallucination(self, package_name: str) -> tuple[bool, str]:
        """Check if package is a known LLM hallucination."""
        if package_name in self.known_hallucinations:
            return True, self.known_hallucinations[package_name]
        return False, ""
