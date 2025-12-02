"""Async OpenAI client wrapper used across the backend."""
from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class LLMClient:
    """Thin wrapper around the OpenAI client with JSON helpers."""

    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("LLM_MODEL", "gpt-4o")
        self._client: Optional[AsyncOpenAI] = AsyncOpenAI(api_key=api_key) if api_key else None

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    async def request_json(self, prompt: str, *, temperature: float = 0.2) -> Dict[str, Any]:
        """Send the prompt to OpenAI and force a JSON object response."""

        if not self._client:
            raise RuntimeError("OPENAI_API_KEY is not configured. Unable to reach OpenAI API.")

        response = await self._client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant that always responds with compact JSON "
                        "matching exactly what the user instructs."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:  # pragma: no cover - defensive branch
            raise ValueError("LLM response was not valid JSON") from exc
