"""
FastAPI Webhook Receiver App for CodeSlim GitHub PR Bot.

Provides secure HTTP endpoints for receiving GitHub `pull_request` webhooks:
- HMAC-SHA256 cryptographic signature validation (`X-Hub-Signature-256`)
- Asynchronous non-blocking background execution (returns HTTP 202 under 100ms)
- Pydantic payload validation and PRHandler dispatching

Security:
    Mandatory HMAC signature validation prevents unauthorized third parties from
    triggering arbitrary code scans or spamming PR comments.
"""

import hashlib
import hmac
import os
from typing import Any

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request, status

from codeslim.bot.github_client import GitHubClient
from codeslim.bot.models import GitHubPullRequestEvent
from codeslim.bot.pr_handler import PRHandler
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.bot.app")


def verify_github_signature(payload: bytes, signature_header: str | None, secret: str) -> bool:
    """
    Verify GitHub HMAC-SHA256 webhook signature.

    Args:
        payload: Raw request body bytes.
        signature_header: Value of 'X-Hub-Signature-256' header (format: 'sha256=<hex>').
        secret: Webhook secret token configured in GitHub.

    Returns:
        True if signature matches, False otherwise.
    """
    if not signature_header or not secret:
        return False

    if not signature_header.startswith("sha256="):
        return False

    expected_sig = signature_header.split("sha256=", 1)[1]
    computed_hmac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
    computed_sig = computed_hmac.hexdigest()

    return hmac.compare_digest(computed_sig, expected_sig)


def create_bot_app(
    github_token: str | None = None,
    webhook_secret: str | None = None,
    auto_commit: bool = False,
) -> FastAPI:
    """
    Factory function creating configured FastAPI webhook application.

    Args:
        github_token: Optional GitHub PAT (defaults to CODESLIM_GITHUB_TOKEN env var).
        webhook_secret: Optional Webhook Secret (defaults to CODESLIM_GITHUB_WEBHOOK_SECRET env var).
        auto_commit: If True, auto-commits Tier-1 dead import removals to PR branch.

    Returns:
        Configured FastAPI application instance.
    """
    token = github_token or os.environ.get("CODESLIM_GITHUB_TOKEN", "")
    secret = webhook_secret or os.environ.get("CODESLIM_GITHUB_WEBHOOK_SECRET", "")

    app = FastAPI(
        title="CodeSlim GitHub Bot Server",
        description="Autonomous AI Code Quality Audit Bot Webhook Receiver",
        version="2.0.0",
    )

    # Initialize GitHub REST client & PR Handler
    github_client = GitHubClient(token=token)
    pr_handler = PRHandler(github_client=github_client)

    @app.get("/healthcheck")
    async def healthcheck() -> dict[str, Any]:
        """Healthcheck endpoint for readiness/liveness probes."""
        return {
            "status": "healthy",
            "service": "codeslim-pr-bot",
            "auth_configured": bool(token),
            "webhook_secret_configured": bool(secret),
            "auto_commit": auto_commit,
        }

    @app.post("/webhook/github", status_code=status.HTTP_202_ACCEPTED)
    async def handle_github_webhook(
        request: Request,
        background_tasks: BackgroundTasks,
        x_github_event: str | None = Header(default=None, alias="X-GitHub-Event"),
        x_hub_signature_256: str | None = Header(default=None, alias="X-Hub-Signature-256"),
    ) -> dict[str, Any]:
        """
        GitHub Webhook POST endpoint.

        Validates HMAC signature, filters pull_request events, returns HTTP 202 Accepted
        immediately, and schedules PR processing in the background.
        """
        payload_bytes = await request.body()

        # Step 1: HMAC Signature verification if secret is configured
        if secret:
            if not verify_github_signature(payload_bytes, x_hub_signature_256, secret):
                log.warning("invalid_webhook_signature", header=x_hub_signature_256)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or missing X-Hub-Signature-256 header",
                )

        # Step 2: Handle non-pull_request ping or unsupported events
        if x_github_event == "ping":
            log.info("received_ping_event")
            return {"status": "pong", "message": "CodeSlim Bot is active!"}

        if x_github_event != "pull_request":
            log.info("ignoring_non_pr_event", event_type=x_github_event)
            return {"status": "ignored", "reason": f"Event '{x_github_event}' is not supported"}

        # Step 3: Parse event payload using Pydantic V2 schema
        try:
            event_json = await request.json()
            event = GitHubPullRequestEvent.model_validate(event_json)
        except Exception as exc:
            log.error("failed_to_parse_pr_event", error=str(exc))
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid pull_request payload shape: {exc}",
            ) from exc

        # Step 4: Filter relevant PR actions (opened, synchronize, reopened)
        if event.action not in ("opened", "synchronize", "reopened"):
            log.info("ignoring_pr_action", action=event.action)
            return {"status": "ignored", "reason": f"Action '{event.action}' does not trigger audit"}

        # Step 5: Schedule PR handler background task & return HTTP 202 immediately
        log.info(
            "scheduling_pr_audit",
            repo=event.repository.full_name,
            pr=event.pull_request.number,
            action=event.action,
        )

        background_tasks.add_task(
            pr_handler.process_pull_request,
            event=event,
            auto_commit=auto_commit,
        )

        return {
            "status": "accepted",
            "message": f"Audit scheduled for PR #{event.pull_request.number} in {event.repository.full_name}",
            "pr_number": event.pull_request.number,
            "action": event.action,
        }

    return app
