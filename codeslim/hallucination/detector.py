"""Main hallucination detector module."""

import importlib.util
from typing import Any

from codeslim.analyzers.ast_analyzer import STDLIB_MODULES
from codeslim.hallucination.pypi_verifier import PyPIVerifier
from codeslim.models.hallucination import HallucinationFinding, HallucinationReport
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.hallucination.detector")


class HallucinationDetector:
    """Verifies import statements for hallucinated or non-existent Python packages."""

    def __init__(self) -> None:
        self.verifier = PyPIVerifier()

    def verify_imports(
        self,
        file_path: str,
        imports: list[dict[str, Any]],
    ) -> HallucinationReport:
        """
        Verify a list of import statements extracted by ASTAnalyzer.

        Args:
            file_path: Path to target Python file.
            imports: List of import dicts from ASTAnalyzer (contains package_to_verify, line, statement).

        Returns:
            Aggregated HallucinationReport with detailed findings.
        """
        findings: list[HallucinationFinding] = []

        for imp in imports:
            pkg = imp.get("package_to_verify") or imp.get("module", "").split(".")[0]
            if not pkg:
                continue

            line = imp.get("line", 1)
            stmt = imp.get("statement", f"import {pkg}")

            # 1. Check stdlib
            if pkg in STDLIB_MODULES:
                findings.append(
                    HallucinationFinding(
                        package_name=pkg,
                        import_line=line,
                        import_statement=stmt,
                        is_hallucinated=False,
                        verification_source="stdlib",
                        confidence=100,
                    )
                )
                continue

            # 2. Check known LLM hallucinations
            is_hallucinated, suggestion = self.verifier.is_known_hallucination(pkg)
            if is_hallucinated:
                findings.append(
                    HallucinationFinding(
                        package_name=pkg,
                        import_line=line,
                        import_statement=stmt,
                        is_hallucinated=True,
                        verification_source="depscope",
                        confidence=100,
                        suggestion=suggestion,
                    )
                )
                continue

            # 3. Check local environment installation
            spec = None
            try:
                spec = importlib.util.find_spec(pkg)
            except Exception:
                spec = None

            if spec is not None:
                findings.append(
                    HallucinationFinding(
                        package_name=pkg,
                        import_line=line,
                        import_statement=stmt,
                        is_hallucinated=False,
                        verification_source="local",
                        confidence=100,
                    )
                )
            else:
                findings.append(
                    HallucinationFinding(
                        package_name=pkg,
                        import_line=line,
                        import_statement=stmt,
                        is_hallucinated=False,
                        verification_source="third_party",
                        confidence=80,
                    )
                )

        log.info(
            "import_verification_complete",
            file=file_path,
            total_imports=len(imports),
            findings_count=len(findings),
        )

        return HallucinationReport(
            file_path=file_path,
            total_imports_checked=len(imports),
            findings=findings,
        )
