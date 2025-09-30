from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from hashlib import md5
from typing import Any, Dict, Iterable, List, Tuple

import openai

PROMPT_TEMPLATE = """
Given a topic, return a JSON object of subtopics for the topic.\n
Return the response as a JSON object with a single key named "subtopics" whose value is a list of concise subtopic strings.\n
Topic: {topic}
""".strip()


class SubtopicGenerationError(RuntimeError):
    """Raised when subtopics cannot be generated."""


@dataclass
class GenerationRequest:
    topics: List[str]
    max_level: int
    temperature: float
    model: str
    use_demo_mode: bool


def generate_topic_tree(
    request: GenerationRequest,
    api_key: str,
) -> Dict[str, Any]:
    """Generate a nested subtopic structure for the provided topics."""

    if not request.topics:
        raise SubtopicGenerationError("At least one topic is required.")

    if request.max_level < 1 or request.max_level > 6:
        raise SubtopicGenerationError("Depth must be between 1 and 6 levels.")

    trees = []
    for topic in request.topics:
        children, metadata = _build_tree(
            topic=topic,
            level=1,
            max_level=request.max_level,
            api_key=api_key,
            temperature=request.temperature,
            model=request.model,
            use_demo_mode=request.use_demo_mode or not api_key,
        )
        tree = {
            "topic": topic,
            "children": children,
            "metadata": metadata or [],
        }
        trees.append(tree)

    return {
        "id": uuid.uuid4().hex,
        "topics": request.topics,
        "max_level": request.max_level,
        "temperature": request.temperature,
        "model": request.model,
        "use_demo_mode": request.use_demo_mode or not api_key,
        "created_at": datetime.utcnow().isoformat(),
        "trees": trees,
    }


def _build_tree(
    topic: str,
    level: int,
    max_level: int,
    api_key: str,
    temperature: float,
    model: str,
    use_demo_mode: bool,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if level > max_level:
        return [], []

    subtopics, metadata = _fetch_subtopics(
        topic=topic,
        api_key=api_key,
        temperature=temperature,
        model=model,
        use_demo_mode=use_demo_mode,
    )

    children: List[Dict[str, Any]] = []
    call_metadata: List[Dict[str, Any]] = []
    for subtopic in subtopics:
        grand_children, call_stats = _build_tree(
            topic=subtopic,
            level=level + 1,
            max_level=max_level,
            api_key=api_key,
            temperature=temperature,
            model=model,
            use_demo_mode=use_demo_mode,
        )
        children.append(
            {
                "topic": subtopic,
                "children": grand_children,
                "metadata": call_stats or [],
            }
        )
        call_metadata.extend(call_stats)

    return children, [metadata] + call_metadata if metadata else call_metadata


def _fetch_subtopics(
    topic: str,
    api_key: str,
    temperature: float,
    model: str,
    use_demo_mode: bool,
) -> Tuple[Iterable[str], Dict[str, Any] | None]:
    if use_demo_mode:
        return _demo_subtopics(topic), {"mode": "demo"}

    if not api_key:
        raise SubtopicGenerationError(
            "No OpenAI API key configured. Provide one in config.py or set OPENAI_API_KEY."
        )

    openai.api_key = api_key
    try:
        start_time = time.monotonic()
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(topic=topic)}],
            temperature=temperature,
        )
        elapsed = time.monotonic() - start_time
    except Exception as exc:  # pragma: no cover - network errors not unit tested
        raise SubtopicGenerationError(str(exc)) from exc

    usage = getattr(response, "usage", None)
    if usage is not None:
        response_metadata = {
            "mode": "live",
            "total_tokens": usage.get("total_tokens"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "elapsed_seconds": round(elapsed, 2),
        }
    else:
        response_metadata = {"mode": "live", "elapsed_seconds": round(elapsed, 2)}

    message = response["choices"][0]["message"]["content"]
    try:
        json_payload = json.loads(message)
    except json.JSONDecodeError as exc:
        raise SubtopicGenerationError("Model returned a non-JSON response.") from exc

    subtopics = json_payload.get("subtopics")
    if not isinstance(subtopics, list):
        raise SubtopicGenerationError("Response JSON does not include a 'subtopics' list.")

    cleaned = [str(item).strip() for item in subtopics if str(item).strip()]

    if not cleaned:
        raise SubtopicGenerationError("No subtopics were returned by the model.")

    return cleaned, response_metadata


def _demo_subtopics(topic: str) -> List[str]:
    """Generate deterministic mock subtopics for demo mode."""
    digest = md5(topic.encode("utf-8"))
    anchors = [
        "Foundations",
        "Applications",
        "Trends",
        "Challenges",
        "Tools",
        "Case Studies",
        "Innovations",
        "Ethics",
        "Careers",
    ]
    offset = int(digest.hexdigest(), 16)
    subtopics = []
    for index in range(3):
        anchor = anchors[(offset + index) % len(anchors)]
        subtopics.append(f"{topic} {anchor}")
    return subtopics
