"""
Async GitHub REST API Client for CodeSlim PR Bot.

Handles authenticated communication with GitHub's REST API v3:
- Fetch list of changed files in a Pull Request
- Download raw file contents for analysis
- Post Markdown comments to PR conversations
- Push auto-fix commits back to the PR branch (opt-in)

Agentic AI Concept — Tool Integration:
    In an agentic pipeline, external APIs act as "tools" that the agent
    invokes to interact with the outside world. This client is the bridge
    between CodeSlim's internal analysis engine and GitHub's ecosystem.
    The agent (PR handler) decides WHEN to call each method based on
    pipeline results — just like a LangGraph agent selects tools based
    on the current state.

Security:
    All requests use a GitHub Personal Access Token (PAT) or GitHub App
    installation token passed via the CODESLIM_GITHUB_TOKEN env var.
    HMAC signature verification happens at the webhook layer (app.py),
    NOT here — this client only handles outbound authenticated requests.
"""

import base64
from typing import Any

import httpx

from codeslim.bot.models import GitHubPRFile
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.bot.github_client")

GITHUB_API_BASE = "https://api.github.com"


class GitHubClient:
    """Async HTTP client for GitHub REST API v3."""

    def __init__(self, token: str) -> None:
        """
        Initialize with a GitHub authentication token.

        Args:
            token: GitHub PAT or App installation token.
        """
        clean_token = token.strip() if token else ""
        self.token = clean_token
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if clean_token:
            self._headers["Authorization"] = f"Bearer {clean_token}"

    async def get_pr_files(self, repo_full_name: str, pr_number: int) -> list[GitHubPRFile]:
        """
        Fetch the list of files changed in a pull request.

        Args:
            repo_full_name: "owner/repo" format.
            pr_number: Pull request number.

        Returns:
            List of GitHubPRFile models for each changed file.
        """
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/pulls/{pr_number}/files"
        log.info("fetching_pr_files", repo=repo_full_name, pr=pr_number)

        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            response = await client.get(url, params={"per_page": 100})
            response.raise_for_status()

        files_data: list[dict[str, Any]] = response.json()
        return [GitHubPRFile.model_validate(f) for f in files_data]

    async def get_file_content(self, repo_full_name: str, file_path: str, ref: str) -> str:
        """
        Download raw file content from a specific branch/commit.

        Args:
            repo_full_name: "owner/repo" format.
            file_path: Path relative to repo root.
            ref: Branch name or commit SHA.

        Returns:
            Raw file content as string.
        """
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/contents/{file_path}"
        log.info("fetching_file_content", repo=repo_full_name, path=file_path, ref=ref)

        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            response = await client.get(url, params={"ref": ref})
            response.raise_for_status()

        data = response.json()
        content_b64: str = data.get("content", "")
        return base64.b64decode(content_b64).decode("utf-8")

    async def post_pr_comment(self, repo_full_name: str, pr_number: int, body: str) -> dict[str, Any]:
        """
        Post a Markdown comment to a PR conversation.

        Args:
            repo_full_name: "owner/repo" format.
            pr_number: Pull request number.
            body: Markdown-formatted comment body.

        Returns:
            GitHub API response dict for the created comment.
        """
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/issues/{pr_number}/comments"
        log.info("posting_pr_comment", repo=repo_full_name, pr=pr_number, body_len=len(body))

        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            response = await client.post(url, json={"body": body})
            response.raise_for_status()

        result: dict[str, Any] = response.json()
        return result

    async def push_file_commit(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        branch: str,
        commit_message: str,
    ) -> dict[str, Any]:
        """
        Push a single-file commit to a branch (for auto-fix Tier-1 changes).

        Uses the GitHub Contents API (PUT /repos/{owner}/{repo}/contents/{path})
        which handles create-or-update atomically. Requires the current file SHA.

        Args:
            repo_full_name: "owner/repo" format.
            file_path: Path relative to repo root.
            content: New file content string.
            branch: Target branch name.
            commit_message: Git commit message.

        Returns:
            GitHub API response dict for the commit.
        """
        url = f"{GITHUB_API_BASE}/repos/{repo_full_name}/contents/{file_path}"
        log.info("pushing_auto_fix_commit", repo=repo_full_name, path=file_path, branch=branch)

        # Step 1: Get current file SHA (required for update)
        async with httpx.AsyncClient(headers=self._headers, timeout=30.0) as client:
            get_resp = await client.get(url, params={"ref": branch})
            get_resp.raise_for_status()
            current_sha: str = get_resp.json()["sha"]

            # Step 2: Push updated content
            encoded_content = base64.b64encode(content.encode("utf-8")).decode("ascii")
            put_resp = await client.put(
                url,
                json={
                    "message": commit_message,
                    "content": encoded_content,
                    "sha": current_sha,
                    "branch": branch,
                },
            )
            put_resp.raise_for_status()

        result: dict[str, Any] = put_resp.json()
        log.info("auto_fix_commit_pushed", sha=result.get("commit", {}).get("sha", "unknown"))
        return result
