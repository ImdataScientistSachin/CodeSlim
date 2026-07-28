"""
Static Analysis Metrics Models for CodeSlim.

Defines Pydantic V2 models for normalized code complexity, dead code,
and composite bloat score calculations.
"""

from pydantic import BaseModel, Field, computed_field


class FunctionMetrics(BaseModel):
    """Metrics for an individual function or method."""

    name: str = Field(description="Function or method name")
    line_start: int = Field(ge=1, description="First line number")
    line_end: int = Field(ge=1, description="Last line number")
    cyclomatic_complexity: int = Field(default=0, ge=0, description="Radon Cyclomatic Complexity score")
    cognitive_complexity: int = Field(default=0, ge=0, description="Lizard Cognitive Complexity score")
    nesting_depth: int = Field(default=0, ge=0, description="Maximum control flow nesting depth")
    parameter_count: int = Field(default=0, ge=0, description="Number of parameters")

    @computed_field
    @property
    def line_count(self) -> int:
        """Total lines spanned by function."""
        return max(1, self.line_end - self.line_start + 1)

    @computed_field
    @property
    def is_complex(self) -> bool:
        """Flag functions exceeding complexity thresholds (CC > 10 or Nesting > 4)."""
        return self.cyclomatic_complexity > 10 or self.nesting_depth > 4


class DeadCodeItem(BaseModel):
    """Dead code finding reported by static analysis."""

    name: str = Field(description="Name of unused symbol or import")
    line: int = Field(ge=1, description="Line number of dead code")
    code_type: str = Field(description="Symbol type: function, import, variable, class")
    confidence: int = Field(default=100, ge=0, le=100, description="Confidence score (0-100%)")
    message: str = Field(default="", description="Finding message")


class FileMetrics(BaseModel):
    """Aggregated static analysis metrics for a Python file."""

    file_path: str = Field(description="Target file path")
    total_lines: int = Field(ge=0, description="Total line count")
    blank_lines: int = Field(default=0, ge=0, description="Blank line count")
    comment_lines: int = Field(default=0, ge=0, description="Comment line count")

    functions: list[FunctionMetrics] = Field(default_factory=list, description="Per-function complexity metrics")
    dead_code: list[DeadCodeItem] = Field(default_factory=list, description="Dead code items")

    total_imports: int = Field(default=0, ge=0, description="Total import statement count")
    third_party_imports: list[str] = Field(default_factory=list, description="Third-party package names")
    stdlib_imports: list[str] = Field(default_factory=list, description="Standard library module names")

    duplication_ratio: float = Field(default=0.0, ge=0.0, le=1.0, description="Duplication fraction (0.0 to 1.0)")

    @computed_field
    @property
    def dead_code_count(self) -> int:
        """Total count of dead code items."""
        return len(self.dead_code)

    @computed_field
    @property
    def max_cyclomatic_complexity(self) -> int:
        """Maximum cyclomatic complexity among all functions in file."""
        if not self.functions:
            return 0
        return max(f.cyclomatic_complexity for f in self.functions)

    @computed_field
    @property
    def max_cc(self) -> int:
        """Alias for max_cyclomatic_complexity."""
        return self.max_cyclomatic_complexity

    @computed_field
    @property
    def max_cognitive_complexity(self) -> int:
        """Maximum cognitive complexity among all functions in file."""
        if not self.functions:
            return 0
        return max(f.cognitive_complexity for f in self.functions)

    @computed_field
    @property
    def max_nesting_depth(self) -> int:
        """Maximum control flow nesting depth among all functions in file."""
        if not self.functions:
            return 0
        return max(f.nesting_depth for f in self.functions)

    @computed_field
    @property
    def complex_function_count(self) -> int:
        """Number of functions exceeding complexity thresholds."""
        return sum(1 for f in self.functions if f.is_complex)

    @computed_field
    @property
    def code_lines(self) -> int:
        """Executable lines of code (total minus blank and comment lines)."""
        return max(0, self.total_lines - self.blank_lines - self.comment_lines)
