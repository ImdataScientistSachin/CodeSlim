"""
Unit tests for Async LLM Client & Fallback Chain.
"""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from codeslim.llm.client import LLMClient, OllamaProvider
from codeslim.llm.models import LLMRefactorResponse


@pytest.mark.asyncio
async def test_ollama_provider_payload_formatting(mocker):
    """Fixes BUG-09: Verify temperature is nested inside `options` dict in Ollama REST payload."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": '```json\n{"summary": "OK", "actions": [], "optimized_code": "pass", "confidence_score": 0.9}\n```'
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_async_client_cls = mocker.patch("httpx.AsyncClient")
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client

    provider = OllamaProvider(base_url="http://localhost:11434", model_name="qwen2.5-coder:3b", temperature=0.1)
    result = await provider.generate("system", "user")

    assert "optimized_code" in result
    mock_client.post.assert_called_once()
    call_kwargs = mock_client.post.call_args[1]
    payload = call_kwargs["json"]
    assert payload["options"]["temperature"] == 0.1
    assert payload["model"] == "qwen2.5-coder:3b"


@pytest.mark.asyncio
async def test_invoke_structured_successful_parse(mocker):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response": json.dumps(
            {
                "summary": "Cleaned dead code",
                "actions": [
                    {
                        "action_type": "remove_dead_code",
                        "target_symbol": "unused",
                        "line_start": 5,
                        "line_end": 5,
                        "explanation": "Unused variable",
                    }
                ],
                "optimized_code": "x = 10",
                "confidence_score": 0.95,
            }
        )
    }
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_async_client_cls = mocker.patch("httpx.AsyncClient")
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client

    client = LLMClient()
    parsed = await client.invoke_structured("system", "user", LLMRefactorResponse)
    assert parsed.summary == "Cleaned dead code"
    assert len(parsed.actions) == 1


@pytest.mark.asyncio
async def test_invoke_structured_escalating_retry_on_json_error(mocker):
    """Fixes BUG-10: Test escalating prompt retry on initial JSON decode error."""
    resp1 = MagicMock()
    resp1.json.return_value = {"response": "invalid json text {"}
    resp1.raise_for_status = MagicMock()

    resp2 = MagicMock()
    resp2.json.return_value = {
        "response": json.dumps(
            {
                "summary": "Fixed JSON",
                "actions": [],
                "optimized_code": "pass",
                "confidence_score": 0.9,
            }
        )
    }
    resp2.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=[resp1, resp2])

    mock_async_client_cls = mocker.patch("httpx.AsyncClient")
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client

    client = LLMClient(max_retries=2)
    parsed = await client.invoke_structured("system", "user", LLMRefactorResponse)
    assert parsed.summary == "Fixed JSON"

    assert mock_client.post.call_count == 2
    second_call_payload = mock_client.post.call_args_list[1][1]["json"]
    assert "[SYSTEM ERROR NOTICE - RETRY ATTEMPT 2/2]" in second_call_payload["prompt"]


@pytest.mark.asyncio
async def test_ollama_provider_with_gbnf_grammar(mocker):
    """Test GBNF grammar parameter passed to Ollama payload for qwen2.5-coder:1.5b."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "def test():\n    return 42"}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_async_client_cls = mocker.patch("httpx.AsyncClient")
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client

    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model_name="qwen2.5-coder:1.5b",
        temperature=0.1,
    )
    result = await provider.generate("sys", "user", grammar="root ::= function_def")

    assert result == "def test():\n    return 42"
    call_kwargs = mock_client.post.call_args[1]
    payload = call_kwargs["json"]
    assert payload["model"] == "qwen2.5-coder:1.5b"
    assert payload["grammar"] == "root ::= function_def"


@pytest.mark.asyncio
async def test_llm_client_auto_applies_python_grammar_for_1_5b(mocker):
    """Test LLMClient automatically applies python function GBNF grammar for qwen2.5-coder:1.5b chunk refactoring."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "def calculate(x):\n    if x < 0:\n        return 0\n    return x"}
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    mock_async_client_cls = mocker.patch("httpx.AsyncClient")
    mock_async_client_cls.return_value.__aenter__.return_value = mock_client

    client = LLMClient(primary_model="qwen2.5-coder:1.5b")
    refactored = await client.refactor_function_chunk(
        function_code="def calculate(x):\n    return x",
        function_name="calculate",
        cc_score=4,
    )

    assert "return x" in refactored
    call_kwargs = mock_client.post.call_args[1]
    payload = call_kwargs["json"]
    assert payload["model"] == "qwen2.5-coder:1.5b"
    assert "grammar" in payload
    assert "root ::=" in payload["grammar"]

