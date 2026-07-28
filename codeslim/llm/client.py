"""
Asynchronous LLM Client & Fallback Chain for CodeSlim.

Provides a unified interface for local Ollama execution and OpenAI cloud fallback.
Enforces structured JSON completions and escalating retry prompts on schema failures.
"""

import hashlib
import json
from typing import TypeVar

import httpx
from pydantic import BaseModel

from codeslim.config import get_settings
from codeslim.utils.logger import get_logger

log = get_logger("codeslim.llm.client")

T = TypeVar("T", bound=BaseModel)


class OllamaProvider:
    """Ollama local LLM API provider."""

    def __init__(self, base_url: str, model_name: str, temperature: float = 0.1) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.temperature = temperature

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Send generation request to Ollama endpoint.
        Fixes BUG-09: Passes temperature inside `options` dictionary per Ollama REST spec.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": f"{system_prompt}\n\n{user_prompt}",
            "stream": False,
            "options": {
                "temperature": self.temperature,
            },
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()


class OpenAIProvider:
    """OpenAI cloud LLM API provider."""

    def __init__(self, api_key: str | None, model_name: str = "gpt-4o-mini", temperature: float = 0.1) -> None:
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Send completion request to OpenAI API."""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=self.api_key)
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
            )
            return response.choices[0].message.content or ""
        except ImportError as exc:
            raise RuntimeError("openai package not installed. Install with `pip install openai`") from exc


class LLMClient:
    """
    Main LLM client facade for CodeSlim.
    Supports local-first Ollama execution with OpenAI cloud fallback.
    """

    def __init__(
        self,
        temperature: float = 0.1,
        primary_model: str | None = None,
        fallback_model: str = "gpt-4o-mini",
        max_retries: int = 3,
    ) -> None:
        self.settings = get_settings()
        self.temperature = temperature
        self.primary_model = primary_model or self.settings.llm_model_optimization
        self.fallback_model = fallback_model
        self.max_retries = max_retries

        self.ollama = OllamaProvider(
            base_url=self.settings.ollama_base_url,
            model_name=self.primary_model,
            temperature=self.temperature,
        )
        self.openai = OpenAIProvider(
            api_key=self.settings.openai_api_key,
            model_name=self.fallback_model,
            temperature=self.temperature,
        )

    def _generate_cache_key(self, system_prompt: str, user_prompt: str) -> str:
        """SHA-256 hash key generation for cache security."""
        combined = f"{self.primary_model}:{self.temperature}:{system_prompt}:{user_prompt}"
        return hashlib.sha256(combined.encode("utf-8")).hexdigest()

    async def invoke(self, system_prompt: str, user_prompt: str) -> str:
        """
        Execute completion prompt with local-first fallback logic.
        """
        try:
            log.info("invoking_ollama_primary", model=self.primary_model)
            return await self.ollama.generate(system_prompt, user_prompt)
        except Exception as exc:
            log.warning("ollama_primary_failed_falling_back", error=str(exc))
            if self.settings.openai_api_key:
                log.info("invoking_openai_fallback", model=self.fallback_model)
                return await self.openai.generate(system_prompt, user_prompt)
            raise RuntimeError(f"Ollama execution failed and OpenAI API key not configured: {exc}") from exc

    async def refactor_function_chunk(
        self,
        function_code: str,
        function_name: str,
        cc_score: int,
    ) -> str:
        """
        Refactor a single extracted function using a focused prompt.

        Sends only the function body (not the whole file), which dramatically
        improves 3B model compliance and prevents class header deletion.

        Returns:
            Refactored function source code string, or original if LLM fails.
        """
        system_prompt = (
            "You are a Python refactoring expert. "
            "Refactor ONLY the given function to reduce cyclomatic complexity. "
            "Return ONLY the refactored function Python code. "
            "Do NOT add imports. Do NOT rename the function. "
            "Preserve the exact function signature."
        )
        user_prompt = (
            f"Refactor this Python function '{function_name}' "
            f"(current Cyclomatic Complexity: {cc_score}).\n"
            f"Use guard clauses and early returns to flatten nesting.\n\n"
            f"```python\n{function_code}\n```\n\n"
            f"Return ONLY the refactored Python function code."
        )
        try:
            raw = await self.invoke(system_prompt, user_prompt)
            cleaned = raw.strip()
            if cleaned.startswith("```python"):
                cleaned = cleaned[9:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return cleaned.strip()
        except Exception as exc:
            log.warning("chunk_refactor_failed", function=function_name, error=str(exc))
            return function_code

    async def invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[T],
    ) -> T:
        """
        Execute prompt and parse response into Pydantic model T.
        Escalates prompt with specific JSON error feedback on retries.
        """
        current_user_prompt = user_prompt

        for attempt in range(1, self.max_retries + 1):
            raw_response = await self.invoke(system_prompt, current_user_prompt)

            cleaned_json = raw_response.strip()
            if cleaned_json.startswith("```json"):
                cleaned_json = cleaned_json[7:]
            if cleaned_json.startswith("```"):
                cleaned_json = cleaned_json[3:]
            if cleaned_json.endswith("```"):
                cleaned_json = cleaned_json[:-3]
            cleaned_json = cleaned_json.strip()

            try:
                data = json.loads(cleaned_json)
                return response_model(**data)
            except (json.JSONDecodeError, Exception) as parse_exc:
                log.warning(
                    "structured_parsing_failed",
                    attempt=attempt,
                    max_retries=self.max_retries,
                    error=str(parse_exc),
                )
                if attempt == self.max_retries:
                    model_name = response_model.__name__
                    raise ValueError(
                        f"Failed to parse LLM response into {model_name} after {self.max_retries} attempts: {parse_exc}"
                    ) from parse_exc

                current_user_prompt = (
                    f"{user_prompt}\n\n"
                    f"[SYSTEM ERROR NOTICE - RETRY ATTEMPT {attempt + 1}/{self.max_retries}]\n"
                    f"Your previous response failed JSON schema validation with error: {parse_exc}.\n"
                    f"Please respond ONLY with valid JSON matching the exact schema without additional commentary."
                )

        raise ValueError(
            f"Failed to parse LLM response into {response_model.__name__} after {self.max_retries} attempts"
        )
