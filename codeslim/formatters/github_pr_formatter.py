"""
GitHub PR Comment Formatter for CodeSlim.

Renders CodeSlimReport objects as GitHub-Flavored Markdown for PR comments.
"""

from codeslim.models.report import CodeSlimReport


def format_github_pr_report(report: CodeSlimReport) -> str:
    """
    Format CodeSlimReport as Markdown suitable for GitHub PR comments.

    Args:
        report: CodeSlimReport model instance.

    Returns:
        GitHub Markdown string.
    """
    opt_lines = report.optimized_lines or report.original_lines
    lines = [
        f"## 🚀 CodeSlim Analysis Summary: `{report.file_path}`",
        "",
        f"- **Bloat Score**: `{report.bloat_score:.1f}/100.0` (Grade **{report.bloat_grade}**)",
        f"- **Lines Saved**: `{report.lines_saved}` ({report.reduction_percentage}%)",
        f"- **Original Lines**: `{report.original_lines}` $\rightarrow$ **Optimized**: `{opt_lines}`",
        "",
    ]

    if report.bloat_map:
        lines.extend(
            [
                "### ⚠️ Identified Bloat Areas",
                "",
                "| Type | Severity | Lines | Explanation | Suggestion |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )
        for item in report.bloat_map:
            line_range = f"{item.line_start}-{item.line_end}"
            lines.append(
                f"| `{item.bloat_type}` | `{item.severity}` | `{line_range}` | {item.explanation} | {item.suggestion} |"
            )
        lines.append("")

    if report.diff:
        lines.extend(
            [
                "<details>",
                "<summary>🔍 Click to view Unified Diff Preview</summary>",
                "",
                "```diff",
                report.diff,
                "```",
                "",
                "</details>",
                "",
            ]
        )

    lines.append("_Generated automatically by CodeSlim Agentic Refactoring Engine_")
    return "\n".join(lines)
