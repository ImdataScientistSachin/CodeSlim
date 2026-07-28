"""
Unit tests for codeslim.bot.pr_handler — PR Handler & Markdown Comment Generator.
"""

from unittest.mock import AsyncMock

import pytest

from codeslim.bot.models import (
    GitHubPRFile,
    GitHubPRHead,
    GitHubPullRequestEvent,
    GitHubRepo,
    GitHubUser,
)
from codeslim.bot.pr_handler import PRHandler, format_pr_markdown_report
from codeslim.models.report import BloatMapEntry, CodeSlimReport


def _sample_pr_event() -> GitHubPullRequestEvent:
    user = GitHubUser(id=1, login="dev_user")
    repo = GitHubRepo(name="demo-repo", full_name="dev_user/demo-repo", owner=user)
    head = GitHubPRHead(ref="feature/bot-test", sha="head_sha_999")
    pr_data = {
        "number": 42,
        "state": "open",
        "title": "Add feature",
        "user": user,
        "head": head,
    }
    return GitHubPullRequestEvent(
        action="opened",
        number=42,
        pull_request=pr_data,
        repository=repo,
        sender=user,
    )


def test_format_pr_markdown_report_empty():
    report_md = format_pr_markdown_report("owner/repo", 42, [])
    assert "No Python source files were modified" in report_md


def test_format_pr_markdown_report_with_files():
    file_rep = CodeSlimReport(
        file_path="main.py",
        bloat_score=45.0,
        original_lines=100,
        bloat_map=[
            BloatMapEntry(
                line_start=10,
                line_end=10,
                bloat_type="dead_import",
                explanation="Unused import sys",
                suggestion="Remove sys",
                severity="high",
            )
        ],
        diff="--- a/main.py\n+++ b/main.py\n-import sys",
    )
    report_md = format_pr_markdown_report("owner/repo", 42, [file_rep])

    assert "## 🚀 CodeSlim AI Code Quality Audit Report" in report_md
    assert "`owner/repo`" in report_md
    assert "`main.py`" in report_md
    assert "Grade C" in report_md or "`C`" in report_md
    assert "Unused import sys" in report_md
    assert "--- a/main.py" in report_md


@pytest.mark.asyncio
async def test_pr_handler_process_no_py_files():
    mock_github = AsyncMock()
    mock_github.get_pr_files.return_value = [
        GitHubPRFile(filename="README.md", status="modified", sha="sha1")
    ]
    mock_github.post_pr_comment.return_value = {"html_url": "http://github.com/pr/42#comment-1"}

    handler = PRHandler(github_client=mock_github)
    event = _sample_pr_event()

    result = await handler.process_pull_request(event, auto_commit=False)

    assert result["status"] == "success"
    assert result["python_files_analyzed"] == 0
    assert result["comment_url"] == "http://github.com/pr/42#comment-1"
    mock_github.get_pr_files.assert_called_once_with("dev_user/demo-repo", 42)
    mock_github.post_pr_comment.assert_called_once()


@pytest.mark.asyncio
async def test_pr_handler_process_py_file():
    mock_github = AsyncMock()
    mock_github.get_pr_files.return_value = [
        GitHubPRFile(filename="src/app.py", status="modified", sha="sha_app")
    ]
    mock_github.get_file_content.return_value = "import sys\nimport os\nprint('hello')\n"
    mock_github.post_pr_comment.return_value = {"html_url": "http://github.com/pr/42#comment-2"}

    mock_orchestrator = AsyncMock()
    mock_orchestrator.run_pipeline.return_value = CodeSlimReport(
        file_path="src/app.py",
        bloat_score=10.0,
        original_lines=3,
        optimized_code="import os\nprint('hello')\n",
    )

    handler = PRHandler(github_client=mock_github, orchestrator=mock_orchestrator)
    event = _sample_pr_event()

    result = await handler.process_pull_request(event, auto_commit=True)

    assert result["status"] == "success"
    assert result["python_files_analyzed"] == 1
    assert result["auto_commits_pushed"] == 1
    mock_github.get_file_content.assert_called_once_with("dev_user/demo-repo", "src/app.py", ref="head_sha_999")
    mock_github.post_pr_comment.assert_called_once()
    mock_github.push_file_commit.assert_called_once()
