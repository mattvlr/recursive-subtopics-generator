from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from flask import Flask

try:
    import config  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    config = None  # type: ignore

from .services.models import fetch_available_models
from .settings import DEFAULT_SETTINGS, SettingsStore, load_settings, mask_api_key


def create_app(test_config: Dict[str, Any] | None = None) -> Flask:
    """Application factory for the recursive subtopics generator UI."""

    app = Flask(__name__, instance_relative_config=True)

    default_config: Dict[str, Any] = {
        "SECRET_KEY": os.environ.get("FLASK_SECRET_KEY", "dev"),
        "OPENAI_API_KEY": os.environ.get(
            "OPENAI_API_KEY",
            getattr(config, "API_KEY", ""),
        ),
        "HISTORY_PATH": Path(app.instance_path) / "history.json",
        "DEFAULT_TOPICS": getattr(config, "DEFAULT_TOPICS", []),
        "SETTINGS_PATH": Path(app.instance_path) / "settings.json",
        "AVAILABLE_MODELS": getattr(
            config,
            "AVAILABLE_MODELS",
            [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo-preview",
            ],
        ),
    }

    if test_config:
        default_config.update(test_config)

    app.config.from_mapping(default_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    history_path: Path = app.config["HISTORY_PATH"]
    if not history_path.exists():
        history_path.write_text("[]", encoding="utf-8")

    settings_path: Path = app.config["SETTINGS_PATH"]
    if not settings_path.exists():
        settings_path.write_text(json.dumps(DEFAULT_SETTINGS, indent=2), encoding="utf-8")

    # Attempt to dynamically retrieve OpenAI models when an API key is available.
    settings_store = SettingsStore(settings_path)
    stored_settings = settings_store.load()
    effective_api_key = stored_settings.get("api_key") or app.config.get("OPENAI_API_KEY", "")
    dynamic_models = fetch_available_models(effective_api_key)
    if dynamic_models:
        app.config["AVAILABLE_MODELS"] = dynamic_models

    from .routes import main_bp

    app.register_blueprint(main_bp)

    @app.template_filter("format_datetime")
    def format_datetime(value: str) -> str:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%b %d, %Y %I:%M %p")

    @app.context_processor
    def inject_defaults() -> Dict[str, Any]:
        settings = load_settings()
        has_configured_key = bool(
            settings.get("api_key") or app.config.get("OPENAI_API_KEY")
        )
        public_settings = {
            key: value
            for key, value in settings.items()
            if key != "api_key"
        }
        public_settings.update(
            {
                "api_key_masked": mask_api_key(settings.get("api_key", "")),
                "has_api_key": has_configured_key,
                "available_models": app.config["AVAILABLE_MODELS"],
            }
        )
        available_models: List[str] = app.config.get("AVAILABLE_MODELS", [])
        default_model = public_settings.get("default_model")
        if available_models and default_model not in available_models:
            public_settings["default_model"] = available_models[0]
        return {
            "default_topics": settings.get("default_topics")
            or _load_default_topics(app),
            "app_settings": public_settings,
        }

    return app


def _load_default_topics(app: Flask) -> List[str]:
    default_topics: List[str] = app.config.get("DEFAULT_TOPICS") or []
    if default_topics:
        return default_topics

    fallback_path = Path(__file__).parent / "data" / "default_topics.json"
    if fallback_path.exists():
        return json.loads(fallback_path.read_text(encoding="utf-8"))
    return []
