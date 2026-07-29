"""
Rich Terminal Report Formatter for CodeSlim.

Renders CodeSlimReport objects into colorful Rich console panels,
bloat score badges (A-F), tables, confidence tiers, and unified diff preview.
"""

from rich.console import Console

from codeslim.models.report import CodeSlimReport

console = Console()


def format_rich_report(report: CodeSlimReport) -> str:
    """
    Format CodeSlimReport as human-friendly terminal text using Rich.

    Args:
        report: CodeSlimReport model instance.

    Returns:
        Formatted terminal string report.
    """
    lines = []

    # Bloat Grade styling
    grade = report.bloat_grade
    color_map = {"A": "green", "B": "blue", "C": "yellow", "D": "magenta", "F": "red"}
    color = color_map.get(grade, "white")

    lines.append(f"\n[bold]Target File:[/bold] [cyan]{report.file_path}[/cyan]")
    lines.append(f"[bold]Bloat Score:[/bold] [{color}]{report.bloat_score:.1f}/100.0 (Grade {grade})[/{color}]")
    opt_lines = report.optimized_lines or report.original_lines
    lines.append(f"[bold]Original Lines:[/bold] {report.original_lines} | [bold]Optimized Lines:[/bold] {opt_lines}")

    if report.confidence_tiers:
        tiers = report.confidence_tiers
        if isinstance(tiers, dict):
            auto_safe = len(tiers.get("auto_safe", []))
            suggest = len(tiers.get("suggest", []))
            flag_only = len(tiers.get("flag_only", []))
        else:
            auto_safe = len(getattr(tiers, "auto_safe", []))
            suggest = len(getattr(tiers, "suggest", []))
            flag_only = len(getattr(tiers, "flag_only", []))

        lines.append(
            f"[bold]Confidence Tiers:[/bold] [green]Auto-Safe ({auto_safe})[/green] | "
            f"[yellow]Suggest ({suggest})[/yellow] | [red]Flag-Only ({flag_only})[/red]"
        )

    if report.bloat_map:
        lines.append("\n[bold yellow]Identified Bloat Areas:[/bold yellow]")
        for entry in report.bloat_map:
            range_str = f"{entry.line_start}-{entry.line_end}"
            sev = entry.severity.upper()
            color = "red" if entry.severity in ("high", "critical") else ("yellow" if entry.severity == "medium" else "cyan")
            lines.append(f"  * [{color}][{sev}][/{color}] Lines {range_str}: {entry.explanation} ({entry.suggestion})")

    if report.diff:
        lines.append("\n[bold green]Unified Diff Preview:[/bold green]\n")
        lines.append(report.diff)

    return "\n".join(lines)
