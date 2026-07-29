"""
Project Observatory Dashboard Formatter for CodeSlim.

Renders multi-file codebase health, file treemaps, top worst offenders,
cross-file intelligence (phantom functions & hallucination spread),
codebase composition fingerprint, token economy, and surgery plan.
"""


from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codeslim.models.project_report import ProjectReport


def render_project_header(report: ProjectReport) -> Panel:
    """Render main top banner for Project Observatory."""
    title = Text()
    title.append("> CODESLIM PROJECT OBSERVATORY", style="bold cyan")
    title.append("  v2.0\n", style="bold green")
    title.append(
        f"Scanning: {report.project_path}  |  {report.total_files} files  |  {report.total_lines:,} lines",
        style="dim white",
    )
    return Panel(title, border_style="cyan", padding=(0, 2))


def render_project_health(report: ProjectReport) -> Panel:
    """Render overall Project Health Score meter bar and grade badge."""
    score = report.overall_bloat_score
    grade = report.overall_grade

    color = "bold green" if score < 30 else ("bold yellow" if score < 60 else "bold red")
    
    # 40-character bar
    filled = int((score / 100.0) * 40)
    bar = "#" * filled + "-" * (40 - filled)

    text = Text()
    text.append("Overall Grade: ", style="bold white")
    text.append(f"{grade}   ", style=color)
    text.append(f"{score:.1f} / 100\n\n", style="bold white")
    
    text.append("  0         25        50        75       100\n", style="dim")
    text.append("  +---------+---------+---------+---------+\n", style="dim")
    text.append(f"  {bar}  ", style=color)
    text.append(f"{score:.1f}%\n\n", style="bold")

    text.append(
        f"  * {report.total_files} files scanned   "
        f"* {report.fingerprint.dead_lines} dead code lines   "
        f"* {len(report.hallucination_spread)} hallucinated package spread\n"
        f"  * {len(report.phantom_functions)} phantom functions   "
        f"* {len(report.cross_file_clones)} cross-file clones",
        style="dim white",
    )

    return Panel(text, title="[bold cyan]> PROJECT HEALTH[/bold cyan]", border_style="cyan")


def render_file_treemap(report: ProjectReport) -> Panel:
    """Render terminal grid treemap visualization for codebase files."""
    if not report.file_reports:
        return Panel(Text("No files to display", style="dim"))

    max_lines = max((r.original_lines for r in report.file_reports), default=1)
    
    text = Text()
    text.append("(block length = LOC | color = bloat severity)\n\n", style="dim")

    for file_rep in report.file_reports[:12]:  # Top 12 files
        bar_len = max(4, int((file_rep.original_lines / max_lines) * 28))
        color = "bold red" if file_rep.bloat_score >= 60 else ("bold yellow" if file_rep.bloat_score >= 35 else "bold green")
        
        name = file_rep.file_name[:24].ljust(24)
        bar = "#" * bar_len
        
        text.append(f"  {name} ", style="dim white")
        text.append(bar, style=color)
        text.append(f"  {file_rep.bloat_score:.1f}\n", style=color)

    text.append("\n  [CRITICAL] Red (>60)   [MODERATE] Yellow (35-60)   [HEALTHY] Green (<35)", style="dim")
    return Panel(text, title="[bold cyan]> FILE TREEMAP[/bold cyan]", border_style="blue")


def render_top_offenders(report: ProjectReport) -> Panel:
    """Render top 5 worst bloated files table."""
    table = Table(box=None, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("File Path", style="bold white", width=25)
    table.add_column("Bloat Score", width=20)
    table.add_column("Score", width=6, justify="right")
    table.add_column("Primary Findings", style="dim white")

    for idx, rep in enumerate(report.top_offenders, 1):
        color = "bold red" if rep.bloat_score >= 60 else ("bold yellow" if rep.bloat_score >= 35 else "bold green")
        filled = int((rep.bloat_score / 100.0) * 16)
        bar = "#" * filled + "-" * (16 - filled)
        
        findings = []
        if rep.max_cc > 10:
            findings.append(f"CC={rep.max_cc}")
        if rep.dead_code_count > 0:
            findings.append(f"{rep.dead_code_count} dead items")
        if rep.duplication_ratio > 0.15:
            findings.append(f"{int(rep.duplication_ratio*100)}% dup")
        
        finding_str = " | ".join(findings) if findings else "Clean"

        table.add_row(
            f"#{idx}",
            rep.file_name[:25],
            Text(bar, style=color),
            Text(f"{rep.bloat_score:.1f}", style=color),
            finding_str,
        )

    return Panel(table, title="[bold cyan]> TOP 5 WORST OFFENDERS[/bold cyan]", border_style="red")


def render_cross_file_intelligence(report: ProjectReport) -> Panel:
    """Render findings visible only at codebase scope (phantom funcs & hallucination spread)."""
    text = Text()

    if report.phantom_functions:
        text.append("PHANTOM FUNCTIONS (Defined, but never imported anywhere in project):\n", style="bold yellow")
        for pf in report.phantom_functions[:3]:
            text.append(f"  * {pf.function_name}()  in  {pf.file_path}:L{pf.line_number}\n", style="dim white")
        text.append("\n")

    if report.hallucination_spread:
        text.append("HALLUCINATION SPREAD (Fake PyPI packages across files):\n", style="bold magenta")
        for pkg, files in list(report.hallucination_spread.items())[:3]:
            text.append(f"  * '{pkg}'  imported in {len(files)} files: {', '.join(files[:3])}\n", style="dim white")
        text.append("\n")

    if not report.phantom_functions and not report.hallucination_spread:
        text.append("  No cross-file infection or phantom functions detected. Codebase is clean! [OK]\n", style="bold green")

    return Panel(text, title="[bold cyan]> CROSS-FILE INTELLIGENCE[/bold cyan]", border_style="magenta")


def render_codebase_fingerprint(report: ProjectReport) -> Panel:
    """Render codebase composition fingerprint stacked bar."""
    fp = report.fingerprint
    text = Text()

    clean_bar = "#" * max(1, int((fp.clean_pct / 100.0) * 24)) if fp.clean_lines > 0 else ""
    dead_bar = "#" * max(1, int((fp.dead_pct / 100.0) * 24)) if fp.dead_lines > 0 else ""
    complex_bar = "#" * max(1, int((fp.complex_pct / 100.0) * 24)) if fp.complex_lines > 0 else ""
    dup_bar = "#" * max(1, int((fp.dup_pct / 100.0) * 24)) if fp.duplicate_lines > 0 else ""

    text.append("Codebase Line Composition:\n\n", style="dim white")
    text.append(f"  Clean Code    {clean_bar:<24}  {fp.clean_lines:,} lines ({fp.clean_pct}%)\n", style="green")
    text.append(f"  Dead Code     {dead_bar:<24}  {fp.dead_lines:,} lines ({fp.dead_pct}%)\n", style="yellow")
    text.append(f"  Complex Code  {complex_bar:<24}  {fp.complex_lines:,} lines ({fp.complex_pct}%)\n", style="red")
    text.append(f"  Duplication   {dup_bar:<24}  {fp.duplicate_lines:,} lines ({fp.dup_pct}%)\n", style="blue")

    return Panel(text, title="[bold cyan]> CODEBASE FINGERPRINT[/bold cyan]", border_style="cyan")


def format_project_dashboard(report: ProjectReport, console: Console | None = None) -> None:
    """
    Main entry point for Project Observatory UI dashboard.
    Renders panels to console in exact layout order.
    """
    con = console or Console()
    con.print(render_project_header(report))
    con.print(render_project_health(report))
    con.print(render_file_treemap(report))
    con.print(render_top_offenders(report))
    con.print(render_cross_file_intelligence(report))
    con.print(render_codebase_fingerprint(report))
