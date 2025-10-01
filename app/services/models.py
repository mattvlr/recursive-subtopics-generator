from __future__ import annotations

from typing import List

import openai


def fetch_available_models(api_key: str | None) -> List[str]:
    """Return a sorted list of chat-capable OpenAI models.

    Falls back to an empty list if no API key is provided or if the
    request to the OpenAI API fails for any reason. Only models whose
    identifiers start with ``gpt-`` are returned since the application
    uses chat completion endpoints for generation.
    """

    if not api_key:
        return []

    openai.api_key = api_key

    try:  # pragma: no cover - network interaction is not unit tested
        response = openai.Model.list()
    except Exception:  # noqa: BLE001 - propagate as graceful fallback
        return []

    candidates = []
    for item in response.get("data", []):
        model_id = item.get("id")
        if isinstance(model_id, str) and model_id.startswith("gpt-"):
            candidates.append(model_id)

    # Remove duplicates while keeping the first occurrence order.
    seen = set()
    unique = [model for model in candidates if not (model in seen or seen.add(model))]
    return sorted(unique)
