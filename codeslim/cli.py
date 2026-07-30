"""
Command Line Interface for CodeSlim.

Provides CLI commands for single-file analysis, optimization, and whole-project scan:
- codeslim analyze <path>
- codeslim optimize <path>
- codeslim scan <path> [--export-html <output.html>]
"""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console

from codeslim import __version__
from codeslim.formatters.github_pr_formatter import format_github_pr_report
from codeslim.formatters.html_exporter import export_html_report
from codeslim.formatters.json_formatter import format_json_report
from codeslim.formatters.project_dashboard import format_project_dashboard
from codeslim.formatters.rich_formatter import format_rich_report
from codeslim.pipeline.orchestrator import PipelineOrchestrator
from codeslim.pipeline.project_orchestrator import ProjectOrchestrator
from codeslim.utils.file_utils import collect_target_files

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

console = Console(force_terminal=True)


@click.group()
@click.version_option(version=__version__, prog_name="codeslim")
def main() -> None:
    """CodeSlim: Context Minimizer & LLM Guardrail CLI Engine."""


@main.command()
@click.argument("target_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["rich", "json", "github_pr"]),
    default="rich",
    help="Output format",
)
@click.option("--max-tokens", type=int, default=4096, help="Max token budget")
def analyze(target_path: Path, output_format: str, max_tokens: int) -> None:
    """Analyze Python file(s) for code bloat, complexity, and dead code."""
    files = [target_path] if target_path.is_file() else collect_target_files(target_path)
    if not files:
        console.print(f"[yellow]No Python source files found at:[/yellow] {target_path}")
        return

    orchestrator = PipelineOrchestrator(max_token_budget=max_tokens)

    for file_path in files:
        report = asyncio.run(orchestrator.run_pipeline(file_path, no_llm=True))

        if output_format == "json":
            click.echo(format_json_report(report))
        elif output_format == "github_pr":
            click.echo(format_github_pr_report(report))
        else:
            console.print(format_rich_report(report))


@main.command()
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--apply", is_flag=True, help="Apply optimized code directly to target file")
@click.option("--backup", is_flag=True, help="Create a .bak backup file before modifying")
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["rich", "json", "github_pr"]),
    default="rich",
    help="Output format",
)
@click.option("--no-llm", is_flag=True, help="Skip LLM invocation node")
def optimize(file_path: Path, apply: bool, backup: bool, output_format: str, no_llm: bool) -> None:
    """Run full post-LLM optimization pipeline on a Python source file."""
    if file_path.is_dir():
        console.print(f"[red]Error:[/red] `optimize` requires a single Python file path, got directory: {file_path}")
        return

    orchestrator = PipelineOrchestrator()
    report = asyncio.run(orchestrator.run_pipeline(file_path, no_llm=no_llm))

    if apply and report.optimized_code and report.optimized_code != file_path.read_text(encoding="utf-8"):
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
            console.print(f"[green]Backup created:[/green] {backup_path}")

        file_path.write_text(report.optimized_code, encoding="utf-8")
        console.print(f"[bold green]Successfully applied optimizations to:[/bold green] {file_path}")

    if output_format == "json":
        click.echo(format_json_report(report))
    elif output_format == "github_pr":
        click.echo(format_github_pr_report(report))
    else:
        console.print(format_rich_report(report))


@main.command()
@click.argument("target_path", type=click.Path(exists=True, path_type=Path))
@click.option("--no-llm", is_flag=True, default=True, help="Skip LLM node for fast static analysis")
@click.option("--export-html", type=click.Path(path_type=Path), default=None, help="Export interactive HTML observatory report")
def scan(target_path: Path, no_llm: bool, export_html: Path | None) -> None:
    """Run CodeSlim Project Observatory scan on an entire directory."""
    project_orchestrator = ProjectOrchestrator()
    project_report = project_orchestrator.scan_directory(str(target_path), no_llm=no_llm)

    format_project_dashboard(project_report, console=console)

    if export_html:
        export_html_report(project_report, export_html)
        console.print(f"\n[bold green]Interactive HTML Observatory exported to:[/bold green] [cyan]{export_html}[/cyan]")


@main.command("install-hooks")
@click.option(
    "--path",
    "-p",
    "target_path",
    type=click.Path(exists=True, path_type=Path),
    default=".",
    help="Target repository directory",
)
def install_hooks(target_path: Path) -> None:
    """Install local Git pre-commit guardrail hook."""
    from codeslim.hooks import install_git_pre_commit_hook

    success = install_git_pre_commit_hook(target_path)
    if success:
        console.print(
            f"[bold green]Successfully installed CodeSlim pre-commit hook into:[/bold green] [cyan]{target_path / '.git' / 'hooks' / 'pre-commit'}[/cyan]"
        )
    else:
        console.print(
            f"[bold red]Error:[/bold red] Target directory [cyan]{target_path}[/cyan] is not a Git repository (no `.git` directory found)."
        )


@main.group()
def bot() -> None:
    """GitHub Auto-Fix PR Webhook Bot commands."""


@bot.command("serve")
@click.option("--host", default="0.0.0.0", help="Host IP to bind web server")
@click.option("--port", default="8000", help="Port to listen for webhooks")
@click.option("--auto-commit", is_flag=True, help="Enable automatic commits for Tier-1 dead code fixes")
def bot_serve(host: str, port: str | int, auto_commit: bool) -> None:
    """Start the CodeSlim GitHub Webhook Bot HTTP server."""
    import os
    import uvicorn

    from codeslim.bot.app import create_bot_app

    final_port = 8000
    env_port = os.environ.get("PORT")
    if env_port:
        try:
            final_port = int(env_port)
        except ValueError:
            pass
    else:
        try:
            final_port = int(port)
        except (ValueError, TypeError):
            final_port = 8000

    env_host = os.environ.get("HOST")
    if env_host:
        host = env_host

    app = create_bot_app(auto_commit=auto_commit)
    console.print(f"[bold cyan]Starting CodeSlim GitHub PR Bot Server on http://{host}:{final_port}...[/bold cyan]")
    uvicorn.run(app, host=host, port=final_port)




@main.command("ui")
@click.option("--host", default="127.0.0.1", help="Host IP address to bind web server")
@click.option("--port", default=8000, type=int, help="Port to listen for web studio")
@click.option("--open-browser/--no-open-browser", default=True, help="Automatically open browser window")
def ui(host: str, port: int, open_browser: bool) -> None:
    """Launch CodeSlim Web Studio Ultimate Edition interactive web workspace."""
    import webbrowser

    import uvicorn

    from codeslim.ui.server import create_ui_app

    app = create_ui_app()
    url = f"http://{host}:{port}"
    console.print(f"[bold cyan]Launching CodeSlim Web Studio Ultimate on {url}...[/bold cyan]")

    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
