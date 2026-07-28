"""Tests for codeslim.bot.models — GitHub Webhook Pydantic Models."""

import pytest
from pydantic import ValidationError

from codeslim.bot.models import (
    GitHubPRFile,
    GitHubPRHead,
    GitHubPullRequestEvent,
    GitHubRepo,
    GitHubUser,
)

# --- Minimal valid payload matching GitHub's actual webhook schema ---
VALID_WEBHOOK_PAYLOAD = {
    "action": "opened",
    "pull_request": {
        "number": 42,
        "title": "Add logging module",
        "state": "open",
        "head": {
            "ref": "feature/add-logging",
            "sha": "abc123def456",
        },
        "user": {"login": "developer1", "id": 12345},
        "changed_files": 3,
        "additions": 50,
        "deletions": 10,
        # GitHub sends many extra fields we don't need
        "merged": False,
        "draft": False,
        "comments": 2,
    },
    "repository": {
        "full_name": "team/codeslim",
        "clone_url": "https://github.com/team/codeslim.git",
        "default_branch": "main",
        # Extra fields GitHub sends
        "id": 99999,
        "private": True,
    },
    # Top-level extras
    "sender": {"login": "developer1", "id": 12345},
    "installation": {"id": 777},
}


class TestGitHubWebhookModels:
    """Validate that webhook payloads parse correctly and extras are ignored."""

    def test_parse_valid_pull_request_event(self) -> None:
        """Full webhook payload parses into structured GitHubPullRequestEvent."""
        event = GitHubPullRequestEvent.model_validate(VALID_WEBHOOK_PAYLOAD)

        assert event.action == "opened"
        assert event.pull_request.number == 42
        assert event.pull_request.title == "Add logging module"
        assert event.pull_request.head.ref == "feature/add-logging"
        assert event.pull_request.head.sha == "abc123def456"
        assert event.pull_request.user.login == "developer1"
        assert event.repository.full_name == "team/codeslim"
        assert event.repository.default_branch == "main"

    def test_extra_fields_are_ignored(self) -> None:
        """GitHub sends many fields we don't model — verify they're silently ignored."""
        event = GitHubPullRequestEvent.model_validate(VALID_WEBHOOK_PAYLOAD)
        # These should NOT raise — extra="ignore" handles them
        assert not hasattr(event, "sender")
        assert not hasattr(event, "installation")

    def test_missing_required_field_raises_validation_error(self) -> None:
        """Missing required fields (action, pull_request, repository) cause ValidationError."""
        with pytest.raises(ValidationError):
            GitHubPullRequestEvent.model_validate({"action": "opened"})

    def test_pr_head_extracts_branch_and_sha(self) -> None:
        """PRHead correctly extracts branch name and commit SHA."""
        head = GitHubPRHead(ref="fix/memory-leak", sha="deadbeef1234")
        assert head.ref == "fix/memory-leak"
        assert head.sha == "deadbeef1234"

    def test_github_user_identity(self) -> None:
        """User model captures login and numeric ID."""
        user = GitHubUser(login="bot-user", id=99)
        assert user.login == "bot-user"
        assert user.id == 99

    def test_github_repo_defaults(self) -> None:
        """Repo model has sensible defaults for optional fields."""
        repo = GitHubRepo(full_name="org/project")
        assert repo.full_name == "org/project"
        assert repo.clone_url == ""
        assert repo.default_branch == "main"


class TestGitHubPRFileModel:
    """Tests for the PR files list response model."""

    def test_parse_pr_file_entry(self) -> None:
        """PR file entry from /pulls/{n}/files API parses correctly."""
        raw = {
            "filename": "codeslim/pipeline/nodes.py",
            "status": "modified",
            "additions": 15,
            "deletions": 3,
            "patch": "@@ -10,3 +10,15 @@\n+new_code()",
            "contents_url": "https://api.github.com/repos/team/codeslim/contents/codeslim/pipeline/nodes.py?ref=abc123",
            # Extra GitHub fields
            "sha": "filesha123",
            "blob_url": "https://github.com/...",
        }
        pr_file = GitHubPRFile.model_validate(raw)

        assert pr_file.filename == "codeslim/pipeline/nodes.py"
        assert pr_file.status == "modified"
        assert pr_file.additions == 15
        assert pr_file.deletions == 3
        assert "new_code()" in pr_file.patch

    def test_pr_file_defaults(self) -> None:
        """PR file with minimal fields uses defaults."""
        pr_file = GitHubPRFile(filename="setup.py", status="added")
        assert pr_file.additions == 0
        assert pr_file.patch == ""
        assert pr_file.contents_url == ""

    def test_synchronize_action_parses(self) -> None:
        """The 'synchronize' action (new push to PR) parses correctly."""
        payload = {**VALID_WEBHOOK_PAYLOAD, "action": "synchronize"}
        event = GitHubPullRequestEvent.model_validate(payload)
        assert event.action == "synchronize"
