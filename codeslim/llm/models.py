"""
LLM Response Models & JSON Schemas for CodeSlim.

Defines Pydantic V2 models for structured LLM refactoring responses.
"""


from pydantic import AliasChoices, BaseModel, Field


class RefactorAction(BaseModel):
    """Individual refactoring action proposed by LLM."""

    action_type: str = Field(
        default="simplify_complexity",
        validation_alias=AliasChoices("action_type", "type", "kind"),
        description="Type of refactoring action",
    )
    target_symbol: str = Field(
        default="code",
        validation_alias=AliasChoices("target_symbol", "symbol", "target", "name"),
        description="Target function, variable, or class name",
    )
    line_start: int = Field(
        default=1,
        ge=1,
        validation_alias=AliasChoices("line_start", "start_line", "start", "line"),
        description="Starting line number",
    )
    line_end: int = Field(
        default=1,
        ge=1,
        validation_alias=AliasChoices("line_end", "end_line", "end"),
        description="Ending line number",
    )
    explanation: str = Field(
        default="",
        validation_alias=AliasChoices("explanation", "reason", "description", "details"),
        description="Rationale for the refactoring action",
    )


class LLMRefactorResponse(BaseModel):
    """Structured LLM response for code refactoring requests."""

    summary: str = Field(
        default="Code refactored and optimized.",
        validation_alias=AliasChoices("summary", "description", "explanation", "overview"),
        description="High-level summary of proposed refactoring changes",
    )
    actions: list[RefactorAction] = Field(
        default_factory=list,
        validation_alias=AliasChoices("actions", "refactorings", "refactoring_actions", "changes"),
        description="List of discrete refactoring actions",
    )
    optimized_code: str = Field(
        default="",
        validation_alias=AliasChoices("optimized_code", "refactored_code", "code", "output"),
        description="Complete refactored Python source code",
    )
    confidence_score: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("confidence_score", "confidence"),
        description="Self-assessed confidence score (0.0 to 1.0)",
    )
