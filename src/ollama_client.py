from __future__ import annotations

import json
import logging
from typing import Any

import ollama

from src.config import Config, ModelConfig

logger = logging.getLogger(__name__)


class ModelJSONError(RuntimeError):
    """Raised when the model fails to return valid JSON after retries."""


class OllamaClient:
    """Client for interacting with Ollama LLM."""

    def __init__(self, cfg: Config) -> None:
        """Initialize the client with configuration."""
        self._model_name = cfg.model.name
        self._temperature = cfg.model.temperature
        self._timeout_seconds = cfg.model.timeout_seconds
        self._json_mode = cfg.model.json_mode
        self._max_retries = cfg.model.max_retries
        self._host = cfg.model.host
        self._client = ollama.Client(host=self._host)

    def health(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            self._client.list()
            return True
        except Exception as e:
            logger.warning("Ollama health check failed: %s", e)
            return False

    def generate_json(self, system: str, user: str) -> dict:
        """Generate JSON response from the model with retry logic."""
        current_system = system

        for attempt in range(self._max_retries + 1):
            response = self._client.chat(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": current_system},
                    {"role": "user", "content": user},
                ],
                format="json" if self._json_mode else None,
                options={"temperature": self._temperature},
            )

            content = _extract_content(response)

            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.warning("JSON decode failed on attempt %d: %s", attempt + 1, e)
                if attempt < self._max_retries:
                    current_system = (
                        system
                        + "\n\nIMPORTANT: Your previous reply was not valid JSON. "
                        "Reply with RAW JSON only. No markdown. No code fences."
                    )
                else:
                    raise ModelJSONError(
                        f"Failed to get valid JSON after {self._max_retries + 1} attempts. "
                        f"Last error: {e}. Last response (first 300 chars): {content[:300]}"
                    ) from e

        # Should never reach here
        raise ModelJSONError("Unexpected exit from retry loop")


def _extract_content(response: Any) -> str:
    """Extract content string from Ollama chat response."""
    # Dict-style response: response["message"]["content"]
    if isinstance(response, dict):
        if "message" in response and "content" in response["message"]:
            return response["message"]["content"]
    # Object-style response: response.message.content
    if hasattr(response, "message") and hasattr(response.message, "content"):
        return response.message.content

    raise ValueError(f"Unexpected response format: {type(response)}")