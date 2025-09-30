from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List

from flask import current_app

DEFAULT_SETTINGS: Dict[str, Any] = {
    "api_key": "",
    "default_model": "gpt-3.5-turbo",
    "default_depth": 3,
    "default_temperature": 0.2,
    "default_demo_mode": False,
    "default_topics": [],
}


class SettingsStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, Any]:
        if not self.path.exists():
            return DEFAULT_SETTINGS.copy()

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return DEFAULT_SETTINGS.copy()

        normalized = DEFAULT_SETTINGS.copy()
        normalized.update({k: v for k, v in data.items() if k in DEFAULT_SETTINGS})
        normalized["default_topics"] = _ensure_topic_list(normalized.get("default_topics"))
        normalized["default_temperature"] = _clamp_float(
            normalized.get("default_temperature"),
            minimum=0.0,
            maximum=1.0,
            fallback=DEFAULT_SETTINGS["default_temperature"],
        )
        normalized["default_depth"] = _clamp_int(
            normalized.get("default_depth"),
            minimum=1,
            maximum=6,
            fallback=DEFAULT_SETTINGS["default_depth"],
        )
        normalized["default_demo_mode"] = bool(normalized.get("default_demo_mode", False))
        normalized["api_key"] = str(normalized.get("api_key", ""))
        normalized["default_model"] = str(normalized.get("default_model", DEFAULT_SETTINGS["default_model"]))
        return normalized

    def save(self, payload: Dict[str, Any]) -> None:
        current = self.load()
        current.update({k: v for k, v in payload.items() if k in DEFAULT_SETTINGS})
        current["default_topics"] = _ensure_topic_list(payload.get("default_topics", current["default_topics"]))
        current["default_temperature"] = _clamp_float(
            payload.get("default_temperature", current["default_temperature"]),
            minimum=0.0,
            maximum=1.0,
            fallback=current["default_temperature"],
        )
        current["default_depth"] = _clamp_int(
            payload.get("default_depth", current["default_depth"]),
            minimum=1,
            maximum=6,
            fallback=current["default_depth"],
        )
        current["default_demo_mode"] = bool(payload.get("default_demo_mode", False))
        current["api_key"] = str(payload.get("api_key", current["api_key"])).strip()
        current["default_model"] = str(payload.get("default_model", current["default_model"])).strip()
        self.path.write_text(json.dumps(current, indent=2), encoding="utf-8")


def get_settings_store() -> SettingsStore:
    return SettingsStore(Path(current_app.config["SETTINGS_PATH"]))


def load_settings() -> Dict[str, Any]:
    return get_settings_store().load()


def mask_api_key(value: str) -> str:
    value = value.strip()
    if not value:
        return "Not set"
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:4]}…{value[-2:]}"


def _ensure_topic_list(value: Any) -> List[str]:
    if not value:
        return []
    if isinstance(value, str):
        candidates = [segment.strip() for segment in value.replace("\r", "\n").split("\n")]
    elif isinstance(value, list):
        candidates = [str(item).strip() for item in value]
    else:
        return []
    return [item for item in candidates if item]


def _clamp_int(value: Any, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def _clamp_float(value: Any, minimum: float, maximum: float, fallback: float) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return fallback
    parsed = max(minimum, min(maximum, parsed))
    return round(parsed, 2)
