"""
Pull Request Handler for CodeSlim GitHub Bot.

Processes changed Python files in GitHub Pull Requests, runs them through
the CodeSlim PipelineOrchestrator, generates inline GitHub Markdown reports,
and handles optional Tier-1 (Auto-Safe) automated git commits.
"""

import tempfile
from pathlib import Path
from typing import Any

from codeslim.bot.github_client import GitHubClient
from codeslim.bot.models import GitHubPullRequestEvent
from codeslim.models.report import CodeSlimReport
from codeslim.pipeline.orchestrator import PipelineOrchestrator
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.bot.pr_handler")


def format_pr_markdown_report(
    repo_name: str,
    pr_number: int,
    file_reports: list[CodeSlimReport],
) -> str:
    """
    Format aggregated file reports into GitHub Markdown comment format.

    Args:
        repo_name: Repository full name (e.g., 'owner/repo').
        pr_number: Pull request number.
        file_reports: List of analyzed CodeSlimReport objects.

    Returns:
        Formatted GitHub Markdown string.
    """
    if not file_reports:
        return "## 🚀 CodeSlim Audit Report\n\nNo Python source files were modified in this PR."

    total_files = len(file_reports)
    avg_score = sum(r.bloat_score for r in file_reports) / total_files if total_files > 0 else 0.0
    overall_grade = "A" if avg_score < 15 else ("B" if avg_score < 30 else ("C" if avg_score < 50 else "F"))

    lines = [
        "## 🚀 CodeSlim AI Code Quality Audit Report",
        f"**Repository:** `{repo_name}` | **PR:** `#{pr_number}` | **Files Analyzed:** {total_files} | **Grade:** `{overall_grade}` ({avg_score:.1f}/100)",
        "",
        "### 📊 File Summary Matrix",
        "| File Path | Grade | Bloat Score | Lines | Dead Items | Max CC | Status |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]

    for rep in file_reports:
        status_icon = "✅ Clean" if rep.bloat_score < 30 else ("⚠️ Moderate" if rep.bloat_score < 50 else "❌ High Bloat")
        max_cc = rep.metrics.max_cc if rep.metrics else 0
        dead_count = len(rep.metrics.dead_code) if rep.metrics else 0
        lines.append(
            f"| `{rep.file_path}` | `{rep.bloat_grade}` | {rep.bloat_score:.1f} | {rep.original_lines} | {dead_count} | {max_cc} | {status_icon} |"
        )

    lines.append("")
    lines.append("### 🔍 Identified Bloat & Refactoring Suggestions")

    has_details = False
    for rep in file_reports:
        if rep.bloat_map:
            has_details = True
            lines.append(f"<details><summary><strong>{rep.file_path}</strong> — {len(rep.bloat_map)} findings</summary>\n")
            lines.append("| Line Range | Severity | Explanation | Recommendation |")
            lines.append("| :--- | :---: | :--- | :--- |")
            for entry in rep.bloat_map:
                sev_badge = "🔴 HIGH" if entry.severity == "high" else "🟡 MEDIUM"
                lines.append(
                    f"| L{entry.line_start}-L{entry.line_end} | {sev_badge} | {entry.explanation} | {entry.suggestion} |"
                )
            if rep.diff:
                lines.append("\n```diff")
                lines.append(rep.diff[:1500])  # Cap diff length for GitHub comment limit
                if len(rep.diff) > 1500:
                    lines.append("\n... [diff truncated for comment length]")
                lines.append("```")
            lines.append("</details>\n")

    if not has_details:
        lines.append("✨ No bloat issues or cyclomatic complexity warnings detected across modified files!")

    lines.append("\n---")
    lines.append("*Report generated automatically by CodeSlim Agentic AI Guardrail Bot.*")

    return "\n".join(lines)


class PRHandler:
    """
    Orchestrates Pull Request analysis, GitHub comment posting, and automated fixes.
    """

    def __init__(
        self,
        github_client: GitHubClient,
        orchestrator: PipelineOrchestrator | None = None,
    ) -> None:
        """
        Initialize PRHandler with GitHubClient and PipelineOrchestrator.

        Args:
            github_client: Async REST client for GitHub API.
            orchestrator: Optional PipelineOrchestrator instance.
        """
        self.github_client = github_client
        self.orchestrator = orchestrator or PipelineOrchestrator()

    async def process_pull_request(
        self,
        event: GitHubPullRequestEvent,
        auto_commit: bool = False,
    ) -> dict[str, Any]:
        """
        Process a GitHub Pull Request event payload end-to-end.

        Args:
            event: Parsed GitHubPullRequestEvent payload.
            auto_commit: If True, auto-commits Tier-1 dead import removals back to PR branch.

        Returns:
            Dict containing processing status, reports, comment response, and commit info.
        """
        repo_full_name = event.repository.full_name
        pr_number = event.pull_request.number
        head_sha = event.pull_request.head.sha
        branch = event.pull_request.head.ref

        log.info("processing_pr_event", repo=repo_full_name, pr=pr_number, sha=head_sha)

        # Step 1: Fetch changed files in PR via GitHub API
        changed_files = await self.github_client.get_pr_files(repo_full_name, pr_number)
        py_files = [f for f in changed_files if f.filename.endswith(".py") and f.status != "removed"]

        if not py_files:
            log.info("no_python_files_in_pr", pr=pr_number)
            comment_body = "## 🚀 CodeSlim Audit Report\n\nNo active Python source files were modified in this PR."
            comment_resp = await self.github_client.post_pr_comment(repo_full_name, pr_number, comment_body)
            return {
                "status": "success",
                "python_files_analyzed": 0,
                "comment_url": comment_resp.get("html_url"),
                "auto_commits_pushed": 0,
            }

        # Step 2: Analyze each file using temporary local files
        file_reports: list[CodeSlimReport] = []
        auto_commit_files: dict[str, str] = {}

        for pr_file in py_files:
            try:
                content = await self.github_client.get_file_content(repo_full_name, pr_file.filename, ref=head_sha)

                # Write to temp file for PipelineOrchestrator
                with tempfile.NamedTemporaryFile(suffix=".py", mode="w", encoding="utf-8", delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = Path(tmp.name)

                try:
                    report: CodeSlimReport = await self.orchestrator.run_pipeline(tmp_path, no_llm=True)
                    report.file_path = pr_file.filename  # Override temp path with real repo path
                    file_reports.append(report)

                    if auto_commit and report.optimized_code and report.optimized_code != content:
                        auto_commit_files[pr_file.filename] = report.optimized_code
                finally:
                    tmp_path.unlink(missing_ok=True)

            except Exception as exc:
                log.error("pr_file_analysis_failed", file=pr_file.filename, error=str(exc))

        # Step 3: Post formatted Markdown comment to PR conversation thread
        markdown_report = format_pr_markdown_report(repo_full_name, pr_number, file_reports)
        comment_resp = await self.github_client.post_pr_comment(repo_full_name, pr_number, markdown_report)

        # Step 4: Handle optional automated commit of Tier-1 (Auto-Safe) dead code fixes
        committed_count = 0
        if auto_commit and auto_commit_files:
            for filename, opt_code in auto_commit_files.items():
                try:
                    await self.github_client.push_file_commit(
                        repo_full_name=repo_full_name,
                        file_path=filename,
                        content=opt_code,
                        branch=branch,
                        commit_message=f"[codeslim-bot] Auto-fix: remove dead imports in {filename}",
                    )
                    committed_count += 1
                except Exception as exc:
                    log.error("auto_commit_failed", file=filename, error=str(exc))

        return {
            "status": "success",
            "python_files_analyzed": len(file_reports),
            "comment_url": comment_resp.get("html_url"),
            "auto_commits_pushed": committed_count,
        }
