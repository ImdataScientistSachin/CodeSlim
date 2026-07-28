"""
Unit tests for codeslim.bot.app — FastAPI Webhook Receiver & HMAC Verification.
"""

import hashlib
import hmac
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from codeslim.bot.app import create_bot_app, verify_github_signature


def test_verify_github_signature_valid():
    secret = "my_super_secret"
    payload = b'{"action": "opened"}'
    computed_sig = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    header = f"sha256={computed_sig}"

    assert verify_github_signature(payload, header, secret) is True


def test_verify_github_signature_invalid():
    secret = "my_super_secret"
    payload = b'{"action": "opened"}'
    header = "sha256=invalid_hex_signature"

    assert verify_github_signature(payload, header, secret) is False
    assert verify_github_signature(payload, None, secret) is False
    assert verify_github_signature(payload, "invalid_prefix", secret) is False


def test_healthcheck_endpoint():
    app = create_bot_app(github_token="test_token", webhook_secret="test_secret", auto_commit=True)
    client = TestClient(app)

    resp = client.get("/healthcheck")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["auth_configured"] is True
    assert data["webhook_secret_configured"] is True
    assert data["auto_commit"] is True


def test_webhook_ping_event():
    app = create_bot_app(github_token="test_token", webhook_secret="")
    client = TestClient(app)

    headers = {"X-GitHub-Event": "ping"}
    resp = client.post("/webhook/github", json={"zen": "Non-blocking is better than blocking."}, headers=headers)

    assert resp.status_code == 202
    assert resp.json()["status"] == "pong"


def test_webhook_hmac_unauthorized():
    secret = "secret123"
    app = create_bot_app(github_token="test_token", webhook_secret=secret)
    client = TestClient(app)

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=bad_sig",
    }
    resp = client.post("/webhook/github", json={"action": "opened"}, headers=headers)

    assert resp.status_code == 401
    assert "Invalid or missing X-Hub-Signature-256" in resp.json()["detail"]


@patch("codeslim.bot.app.PRHandler")
def test_webhook_pr_opened_schedules_background_task(mock_pr_handler_cls):
    mock_handler_instance = MagicMock()
    mock_pr_handler_cls.return_value = mock_handler_instance

    secret = "secret123"
    app = create_bot_app(github_token="test_token", webhook_secret=secret)
    client = TestClient(app)

    payload = {
        "action": "opened",
        "number": 10,
        "pull_request": {
            "number": 10,
            "title": "PR Title",
            "state": "open",
            "head": {"ref": "feature", "sha": "abc123sha"},
            "user": {"id": 1, "login": "alice"},
        },
        "repository": {"full_name": "alice/my-repo"},
    }
    import json
    payload_bytes = json.dumps(payload).encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": f"sha256={sig}",
    }

    resp = client.post("/webhook/github", content=payload_bytes, headers=headers)

    assert resp.status_code == 202
    data = resp.json()
    assert data["status"] == "accepted"
    assert data["pr_number"] == 10
    assert data["action"] == "opened"
