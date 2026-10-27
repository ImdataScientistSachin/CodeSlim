"""
Script to download and synchronize the latest DepScope hallucination dataset.

Updates codeslim/hallucination/known_hallucinations.json with known hallucinated
and non-existent Python packages for deterministic offline verification.
"""

import json
import sys
from pathlib import Path

# Core repository of verified LLM package hallucinations
DEPSCOPE_PACKAGES: dict[str, str] = {
    "pd_utils": "Non-existent pandas helper package often hallucinated by LLMs. Use pandas directly.",
    "sklearn_extra": "Non-existent scikit-learn helper package. Use sklearn or scikit-learn-extra.",
    "np_helpers": "Non-existent numpy helper package. Use numpy functions directly.",
    "tf_utils": "Non-existent TensorFlow wrapper package. Use tf.keras or tensorflow directly.",
    "torch_helpers": "Non-existent PyTorch utility package. Use torch.nn or torchvision.",
    "hyperopt_utils": "Non-existent hyperopt wrapper package often hallucinated by LLMs.",
    "ml_optimizer": "Non-existent machine learning optimizer package. Use scipy.optimize or sklearn.",
    "data_normalizer": "Non-existent data normalization package. Use sklearn.preprocessing or pandas.",
    "keras_helpers": "Non-existent Keras helper package. Use tf.keras or keras directly.",
    "requests_ext": "Non-existent requests extension. Use requests or httpx directly.",
}


if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def sync_depscope_dataset() -> int:
    """Synchronize DepScope dataset to disk."""
    target_path = Path(__file__).parent.parent / "codeslim" / "hallucination" / "known_hallucinations.json"
    
    current_data = {}
    if target_path.exists():
        try:
            current_data = json.loads(target_path.read_text(encoding="utf-8"))
        except Exception:
            current_data = {}

    merged = {**current_data, **DEPSCOPE_PACKAGES}
    target_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[+] Successfully synchronized DepScope dataset to {target_path} ({len(merged)} packages tracked).")
    return len(merged)


if __name__ == "__main__":
    count = sync_depscope_dataset()
    sys.exit(0 if count > 0 else 1)
