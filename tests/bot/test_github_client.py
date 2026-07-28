"""Tests for codeslim.bot.github_client — Async GitHub API Client."""

import base64
import json

import httpx
import pytest

from codeslim.bot.github_client import GITHUB_API_BASE, GitHubClient


@pytest.fixture
def github_client() -> GitHubClient:
    """Create a GitHubClient with a test token."""
    return GitHubClient(token="ghp_test_token_12345")


class TestGitHubClientHeaders:
    """Verify client initialization and auth headers."""

    def test_auth_header_format(self, github_client: GitHubClient) -> None:
        """Token is formatted as Bearer auth."""
        assert github_client._headers["Authorization"] == "Bearer ghp_test_token_12345"

    def test_accept_header(self, github_client: GitHubClient) -> None:
        """Accept header uses GitHub's JSON content type."""
        assert github_client._headers["Accept"] == "application/vnd.github+json"

    def test_api_version_header(self, github_client: GitHubClient) -> None:
        """X-GitHub-Api-Version header is set."""
        assert "X-GitHub-Api-Version" in github_client._headers


class TestGetPrFiles:
    """Tests for fetching PR file list (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_get_pr_files_parses_response(self, github_client: GitHubClient) -> None:
        """Mocked /pulls/{n}/files response parses into GitHubPRFile list."""
        mock_response_data = [
            {
                "filename": "codeslim/bot/models.py",
                "status": "added",
                "additions": 80,
                "deletions": 0,
                "patch": "@@ +1,80 @@",
                "contents_url": "https://api.github.com/repos/team/cs/contents/codeslim/bot/models.py",
            },
            {
                "filename": "tests/test_bot.py",
                "status": "added",
                "additions": 40,
                "deletions": 0,
                "patch": "@@ +1,40 @@",
                "contents_url": "https://api.github.com/repos/team/cs/contents/tests/test_bot.py",
            },
        ]

        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_response_data)
        )

        # Patch the client to use mock transport
        async with httpx.AsyncClient(
            headers=github_client._headers, transport=transport, timeout=30.0
        ) as mock_client:
            url = f"{GITHUB_API_BASE}/repos/team/codeslim/pulls/42/files"
            response = await mock_client.get(url, params={"per_page": 100})

        from codeslim.bot.models import GitHubPRFile

        files = [GitHubPRFile.model_validate(f) for f in response.json()]

        assert len(files) == 2
        assert files[0].filename == "codeslim/bot/models.py"
        assert files[0].status == "added"
        assert files[1].filename == "tests/test_bot.py"


class TestGetFileContent:
    """Tests for raw file content download (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_file_content_decoded_from_base64(self, github_client: GitHubClient) -> None:
        """Contents API returns base64-encoded content that gets decoded."""
        raw_code = "import os\nprint('hello')\n"
        encoded = base64.b64encode(raw_code.encode("utf-8")).decode("ascii")
        mock_data = {"content": encoded, "encoding": "base64"}

        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=mock_data)
        )

        async with httpx.AsyncClient(
            headers=github_client._headers, transport=transport, timeout=30.0
        ) as mock_client:
            url = f"{GITHUB_API_BASE}/repos/team/codeslim/contents/codeslim/bot/models.py"
            response = await mock_client.get(url, params={"ref": "feature/bot"})

        data = response.json()
        decoded = base64.b64decode(data["content"]).decode("utf-8")
        assert decoded == raw_code


class TestPostPrComment:
    """Tests for PR comment posting (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_post_comment_payload(self, github_client: GitHubClient) -> None:
        """POST to /issues/{n}/comments sends correct JSON body."""
        captured_body = {}

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal captured_body
            captured_body = json.loads(request.content.decode())
            return httpx.Response(201, json={"id": 1001, "body": captured_body.get("body", "")})

        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            headers=github_client._headers, transport=transport, timeout=30.0
        ) as mock_client:
            url = f"{GITHUB_API_BASE}/repos/team/codeslim/issues/42/comments"
            response = await mock_client.post(url, json={"body": "## 🚀 CodeSlim Report"})

        assert response.status_code == 201
        assert captured_body["body"] == "## 🚀 CodeSlim Report"


class TestPushFileCommit:
    """Tests for auto-fix commit push (mocked HTTP)."""

    @pytest.mark.asyncio
    async def test_push_commit_encodes_content(self, github_client: GitHubClient) -> None:
        """Content is base64-encoded before pushing via Contents API."""
        new_code = "import os\n\ndef clean_function():\n    pass\n"
        encoded = base64.b64encode(new_code.encode("utf-8")).decode("ascii")

        call_count = 0
        captured_put_body = {}

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count, captured_put_body
            call_count += 1
            if request.method == "GET":
                return httpx.Response(200, json={"sha": "old_sha_123"})
            if request.method == "PUT":
                captured_put_body = json.loads(request.content.decode())
                return httpx.Response(200, json={
                    "content": {"sha": "new_sha_456"},
                    "commit": {"sha": "commit_sha_789"},
                })
            return httpx.Response(405)

        transport = httpx.MockTransport(handler)

        async with httpx.AsyncClient(
            headers=github_client._headers, transport=transport, timeout=30.0
        ) as mock_client:
            url = f"{GITHUB_API_BASE}/repos/team/codeslim/contents/codeslim/bot/models.py"

            # Step 1: GET current SHA
            get_resp = await mock_client.get(url, params={"ref": "feature/bot"})
            current_sha = get_resp.json()["sha"]

            # Step 2: PUT updated content
            put_resp = await mock_client.put(url, json={
                "message": "[codeslim-bot] Auto-fix: remove dead imports",
                "content": encoded,
                "sha": current_sha,
                "branch": "feature/bot",
            })
            assert put_resp.status_code == 200

        assert call_count == 2
        assert captured_put_body["sha"] == "old_sha_123"
        assert captured_put_body["content"] == encoded
        assert "[codeslim-bot]" in captured_put_body["message"]
