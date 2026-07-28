"""
CodeSlim Test File — Deliberately Bloated AI-Generated Code
Run this through CodeSlim to verify all 4 pipeline stages work.

Patterns included:
  ✅ Over-abstraction (5 classes where 1 function would do)
  ✅ Defensive nesting (8 levels deep)
  ✅ Dead code (unused variables, unreachable branches)
  ✅ Hallucinated imports (fake packages)
  ✅ Redundant computation (repeated calculations)
  ✅ Copy-paste duplication (identical logic blocks)
  ✅ Type over-engineering (complex types for simple data)
"""

import os
import sys
import json
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any, Union

# ── HALLUCINATED IMPORTS (CodeSlim Stage 2 should flag these) ──
import hyperopt_utils        # ❌ Fake package
from ml_optimizer import optimize_pipeline  # ❌ Fake package
import data_normalizer       # ❌ Fake package


# ── OVER-ABSTRACTION: 5 classes where 1 function suffices ──

class InputReader:
    """Reads input. Could be a 3-line function."""

    def __init__(self, path: str):
        self.path = path
        self.content = ""

    def read(self) -> str:
        try:
            with open(self.path, "r") as f:
                self.content = f.read()
            return self.content
        except FileNotFoundError:
            print(f"File not found: {self.path}")
            return ""
        except Exception as e:
            print(f"Error: {e}")
            return ""

    def exists(self) -> bool:
        return os.path.exists(self.path)


class DataParser:
    """Parses data. Exists solely because InputReader exists."""

    def __init__(self, raw: str):
        self.raw = raw
        self.lines: List[str] = []

    def parse_lines(self) -> List[str]:
        self.lines = [l.strip() for l in self.raw.split("\n") if l.strip()]
        return self.lines

    def count_lines(self) -> int:
        return len(self.lines)


class DataValidator:
    """Validates data. One function, promoted to a class."""

    def __init__(self, data: List[str]):
        self.data = data
        self.valid: List[str] = []
        self.invalid: List[str] = []

    def validate_all(self) -> Tuple[List[str], List[str]]:
        for item in self.data:
            if len(item) > 3:
                self.valid.append(item)
            else:
                self.invalid.append(item)
        return self.valid, self.invalid

    def valid_count(self) -> int:
        return len(self.valid)

    def invalid_count(self) -> int:
        return len(self.invalid)


class DataTransformer:
    """Transforms data. Unnecessary extra layer."""

    def __init__(self):
        self.transform_count = 0

    def transform_item(self, item: str) -> str:
        self.transform_count += 1
        return item.upper().replace(" ", "_")

    def transform_all(self, items: List[str]) -> List[str]:
        return [self.transform_item(i) for i in items]


class DataExporter:
    """Exports results. Could be a print() call."""

    def __init__(self, results: List[str]):
        self.results = results

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump({"results": self.results, "count": len(self.results)}, f, indent=2)

    def print_summary(self) -> None:
        print(f"Total: {len(self.results)} items")
        for r in self.results:
            print(f"  - {r}")


# ── DEFENSIVE NESTING HELL (8 levels deep) ──

def deeply_nested(config: dict) -> Optional[str]:
    """Process config with 8 levels of nesting. Classic AI bloat."""

    if config:
        if "enabled" in config:
            if config["enabled"]:
                if "mode" in config:
                    if config["mode"] == "auto":
                        if "threshold" in config:
                            if config["threshold"] > 0:
                                if "output" in config:
                                    if config["output"]:
                                        return config["output"]
                                    else:
                                        return None
                                else:
                                    if "default" in config:
                                        return config["default"]
                                    return None
                            else:
                                return None
                        else:
                            return None
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None
    return None


# ── DEAD CODE (unused function, unused variables) ──

def legacy_compatability_shim() -> None:
    """Dead function — never called anywhere."""
    old_alias_1 = "deprecated"
    old_alias_2 = "also_deprecated"
    print(f"WARNING: {old_alias_1} and {old_alias_2} are deprecated")
    return None


UNUSED_CONSTANT = 42
_LEGACY_FLAG = True
DEPRECATED_REGISTRY: Dict[str, Any] = {}


# ── COPY-PASTE DUPLICATION (identical blocks) ──

def process_user_data(users: List[Dict]) -> List[Dict]:
    """Process user records — block A is copy-pasted as block B."""
    results = []

    # BLOCK A — starts here
    for user in users:
        if user.get("active"):
            name = user.get("name", "unknown")
            email = user.get("email", "")
            role = user.get("role", "viewer")
            score = user.get("score", 0)
            if score > 80:
                tier = "premium"
            elif score > 50:
                tier = "standard"
            else:
                tier = "basic"
            results.append({
                "name": name,
                "email": email,
                "role": role,
                "tier": tier,
            })
    # BLOCK A — ends here

    return results


def process_order_data(orders: List[Dict]) -> List[Dict]:
    """Process order records — identical logic to BLOCK A (copy-paste)."""
    results = []

    # BLOCK B — starts here (identical to BLOCK A)
    for order in orders:
        if order.get("active"):
            name = order.get("name", "unknown")
            email = order.get("email", "")
            role = order.get("role", "viewer")
            score = order.get("score", 0)
            if score > 80:
                tier = "premium"
            elif score > 50:
                tier = "standard"
            else:
                tier = "basic"
            results.append({
                "name": name,
                "email": email,
                "role": role,
                "tier": tier,
            })
    # BLOCK B — ends here (identical to BLOCK A)

    return results


# ── REDUNDANT COMPUTATION ──

def compute_statistics(values: List[float]) -> Dict[str, float]:
    """Compute stats with redundant repeated calculations."""
    total = sum(values)

    # These are computed three times each:
    mean = total / len(values) if values else 0
    mean = sum(values) / len(values) if values else 0                       # Redundant
    mean = total / max(len(values), 1)                                      # Redundant

    variance = sum((x - mean) ** 2 for x in values) / len(values) if values else 0
    std_dev = variance ** 0.5

    # More redundant computation
    min_val = min(values) if values else 0
    max_val = max(values) if values else 0
    min_val = sorted(values)[0] if values else 0                            # Redundant
    max_val = sorted(values)[-1] if values else 0                           # Redundant

    return {
        "mean": mean,
        "median": sorted(values)[len(values) // 2] if values else 0,
        "std_dev": std_dev,
        "min": min_val,
        "max": max_val,
        "count": len(values),
        "sum": total,
        "sum_again": total,                                                  # Redundant
    }


# ── MAIN — uses all the bloat above ──

def main():
    # Write sample data
    with open("/tmp/test_input.txt", "w") as f:
        f.write("apple\nbanana\ncherry\nda\n")

    # 1. Read
    reader = InputReader("/tmp/test_input.txt")
    raw = reader.read()

    # 2. Parse
    parser = DataParser(raw)
    lines = parser.parse_lines()

    # 3. Validate
    validator = DataValidator(lines)
    valid, invalid = validator.validate_all()

    # 4. Transform
    transformer = DataTransformer()
    transformed = transformer.transform_all(valid)

    # 5. Export
    exporter = DataExporter(transformed)
    exporter.print_summary()
    exporter.to_json("/tmp/test_output.json")

    # 6. Nesting test
    config = {"enabled": True, "mode": "auto", "threshold": 5, "output": "done"}
    result = deeply_nested(config)

    # 7. Duplication test
    sample = [
        {"active": True, "name": "Alice", "email": "a@x.com", "role": "admin", "score": 90},
        {"active": True, "name": "Bob", "email": "b@x.com", "role": "user", "score": 60},
    ]
    users = process_user_data(sample)
    orders = process_order_data(sample)

    # 8. Redundant computation test
    stats = compute_statistics([10.0, 20.0, 30.0, 40.0, 50.0])

    print(json.dumps(stats, indent=2))
    print(f"Nesting result: {result}")
    print(f"Users: {len(users)}, Orders: {len(orders)}")
    print(f"Deprecated pipeline: {optimize_pipeline('test')}")  # Uses hallucinated import


if __name__ == "__main__":
    main()
