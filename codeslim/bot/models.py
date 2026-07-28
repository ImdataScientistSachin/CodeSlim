"""
GitHub Webhook Event Models for CodeSlim PR Bot.

Pydantic models that parse incoming GitHub `pull_request` webhook payloads
into type-safe Python objects. Only fields CodeSlim needs are extracted —
the rest are ignored via `model_config = ConfigDict(extra="ignore")`.

Agentic AI Concept — Structured Reasoning:
    These models act as the "input schema" for our bot agent. Just like
    system prompts enforce structured JSON outputs from an LLM, these
    Pydantic schemas enforce structured inputs FROM GitHub webhooks.
    If the payload shape changes, we get an immediate ValidationError
    instead of a silent KeyError bug downstream.
"""

from pydantic import BaseModel, ConfigDict, Field


class GitHubUser(BaseModel):
    """GitHub user identity (PR author or bot actor)."""

    model_config = ConfigDict(extra="ignore")

    login: str
    id: int


class GitHubRepo(BaseModel):
    """Repository metadata extracted from webhook payload."""

    model_config = ConfigDict(extra="ignore")

    full_name: str = Field(description="owner/repo format, e.g. 'user/codeslim'")
    clone_url: str = Field(default="")
    default_branch: str = Field(default="main")


class GitHubPRHead(BaseModel):
    """The head (source) branch of the pull request."""

    model_config = ConfigDict(extra="ignore")

    ref: str = Field(description="Branch name, e.g. 'feature/add-logging'")
    sha: str = Field(description="Latest commit SHA on the PR branch")


class GitHubPullRequest(BaseModel):
    """Core pull request data from the webhook event."""

    model_config = ConfigDict(extra="ignore")

    number: int = Field(description="PR number, e.g. 42")
    title: str = Field(default="")
    state: str = Field(default="open")
    head: GitHubPRHead
    user: GitHubUser
    changed_files: int = Field(default=0)
    additions: int = Field(default=0)
    deletions: int = Field(default=0)


class GitHubPullRequestEvent(BaseModel):
    """
    Top-level GitHub pull_request webhook event payload.

    GitHub sends this JSON body when a PR is opened, synchronized (new push),
    reopened, or closed. We only process 'opened' and 'synchronize' actions.
    """

    model_config = ConfigDict(extra="ignore")

    action: str = Field(description="Event action: opened, synchronize, closed, etc.")
    pull_request: GitHubPullRequest
    repository: GitHubRepo


class GitHubPRFile(BaseModel):
    """
    A single file changed in a PR, from GET /repos/{owner}/{repo}/pulls/{pr}/files.

    This is NOT from the webhook payload — it's fetched separately via the
    GitHub REST API after receiving the webhook event.
    """

    model_config = ConfigDict(extra="ignore")

    filename: str = Field(description="File path relative to repo root")
    status: str = Field(description="added, modified, removed, renamed")
    sha: str = Field(default="", description="Blob SHA of the file")
    additions: int = Field(default=0)
    deletions: int = Field(default=0)
    patch: str = Field(default="", description="Unified diff patch for this file")
    contents_url: str = Field(default="", description="API URL to fetch raw file contents")
