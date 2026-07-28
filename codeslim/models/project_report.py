"""
CodeSlim Project Report Models.

Defines Pydantic data schemas for codebase-level multi-file scanning,
cross-file dependency analysis, and project bloat statistics.
"""

from pydantic import BaseModel, Field, computed_field

from codeslim.models.report import CodeSlimReport


class PhantomFunction(BaseModel):
    """A function defined in a module but never imported or called anywhere in the project."""
    function_name: str
    file_path: str
    line_number: int
    docstring: str = ""


class CrossFileClone(BaseModel):
    """Structurally duplicated logic detected across different files."""
    source_file: str
    target_file: str
    source_function: str
    target_function: str
    similarity_pct: float
    line_count: int


class CodebaseFingerprint(BaseModel):
    """Composition breakdown of lines of code across the entire project."""
    clean_lines: int = 0
    dead_lines: int = 0
    complex_lines: int = 0
    duplicate_lines: int = 0
    hallucinated_import_lines: int = 0
    total_lines: int = 0

    @computed_field
    @property
    def clean_pct(self) -> float:
        return round((self.clean_lines / self.total_lines * 100), 1) if self.total_lines > 0 else 0.0

    @computed_field
    @property
    def bloat_pct(self) -> float:
        return round(100.0 - self.clean_pct, 1)


class ProjectReport(BaseModel):
    """Aggregated codebase analysis report across all files in a project."""
    project_path: str
    total_files: int = 0
    total_lines: int = 0
    overall_bloat_score: float = 0.0
    overall_grade: str = "A"
    
    file_reports: list[CodeSlimReport] = Field(default_factory=list)
    phantom_functions: list[PhantomFunction] = Field(default_factory=list)
    cross_file_clones: list[CrossFileClone] = Field(default_factory=list)
    hallucination_spread: dict[str, list[str]] = Field(default_factory=dict)
    fingerprint: CodebaseFingerprint = Field(default_factory=CodebaseFingerprint)
    stage_timings: dict[str, float] = Field(default_factory=dict)

    @computed_field
    @property
    def top_offenders(self) -> list[CodeSlimReport]:
        """Return the top 5 worst files by bloat score."""
        return sorted(self.file_reports, key=lambda r: r.bloat_score, reverse=True)[:5]
