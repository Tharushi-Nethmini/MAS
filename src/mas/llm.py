from __future__ import annotations

from typing import Any

import requests


def ask_ollama(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    timeout_seconds: int = 60,
) -> str:
    """Call a local Ollama model and return generated text.

    Raises:
        RuntimeError: If Ollama returns a non-200 response or malformed payload.
    """

    endpoint = f"{base_url.rstrip('/')}/api/generate"
    payload: dict[str, Any] = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
    }
    response = requests.post(endpoint, json=payload, timeout=timeout_seconds)
    if response.status_code != 200:
        raise RuntimeError(f"Ollama error {response.status_code}: {response.text}")

    data = response.json()
    text = data.get("response", "")
    if not isinstance(text, str):
        raise RuntimeError("Ollama response field is missing or not a string.")
    return text.strip()
