"""
Unit tests for Function-Level Chunked LLM Refactoring.
"""

from unittest.mock import AsyncMock, patch

import pytest

from codeslim.llm.client import LLMClient


@pytest.mark.asyncio
async def test_refactor_function_chunk():
    client = LLMClient()
    
    raw_fn = "def deeply_nested(x):\n    if x:\n        if x > 10:\n            return True\n    return False"
    refactored_fn = "def deeply_nested(x):\n    if not x or x <= 10:\n        return False\n    return True"

    with patch.object(client, "invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = f"```python\n{refactored_fn}\n```"
        result = await client.refactor_function_chunk(
            function_code=raw_fn,
            function_name="deeply_nested",
            cc_score=11,
        )

    assert "deeply_nested" in result
    assert mock_invoke.called
