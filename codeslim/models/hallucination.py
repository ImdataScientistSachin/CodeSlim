"""
Hallucination Finding Models for CodeSlim.

Defines Pydantic models for package verification findings and file-level hallucination reports.
"""

from pydantic import BaseModel, Field


class HallucinationFinding(BaseModel):
    """Import verification result for a single package."""

    package_name: str = Field(description="Package name extracted from import")
    import_line: int = Field(ge=1, description="Line number of import statement")
    import_statement: str = Field(description="Raw import statement string")
    is_hallucinated: bool = Field(description="True if package is non-existent in registry")
    verification_source: str = Field(
        description="Verification method: stdlib, depscope, cache_hit, pypi_api, npm_api, local"
    )
    confidence: int = Field(default=100, ge=0, le=100, description="Verdict confidence percentage")
    suggestion: str = Field(default="", description="Suggested fix or replacement")


class HallucinationReport(BaseModel):
    """File-level aggregated hallucination check report."""

    file_path: str = Field(description="Target file path")
    total_imports_checked: int = Field(default=0, ge=0, description="Total verified import count")
    findings: list[HallucinationFinding] = Field(default_factory=list, description="Verification findings")

    @property
    def hallucinated_count(self) -> int:
        """Count of confirmed hallucinated packages."""
        return sum(1 for f in self.findings if f.is_hallucinated)

    @property
    def verified_count(self) -> int:
        """Count of confirmed existing packages."""
        return sum(1 for f in self.findings if not f.is_hallucinated)

    @property
    def has_hallucinations(self) -> bool:
        """True if any hallucinated imports were found."""
        return self.hallucinated_count > 0
