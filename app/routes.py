from __future__ import annotations

import json
from typing import Any, Dict, List

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from .services.subtopics import GenerationRequest, SubtopicGenerationError, generate_topic_tree
from .settings import get_settings_store, load_settings, mask_api_key
from .storage import get_store

main_bp = Blueprint("main", __name__)


def _parse_topics(raw_topics: str, default_topics: List[str]) -> List[str]:
    if not raw_topics.strip():
        return default_topics

    separators = [",", "\n", "\r"]
    topics = [raw_topics]
    for sep in separators:
        topics = sum([segment.split(sep) for segment in topics], [])
    cleaned = [topic.strip() for topic in topics if topic.strip()]
    return list(dict.fromkeys(cleaned))


@main_bp.route("/")
def dashboard() -> str:
    store = get_store()
    entries = store.load()
    for entry in entries:
        if entry.get("summary") is None and entry.get("id"):
            summary = _summarize_trees(entry.get("trees", []))
            entry["summary"] = summary
            store.update_entry(entry["id"], {"summary": summary})
    history_entries = entries[:5]
    favorite_entries = [entry for entry in entries if entry.get("is_favorite")][:3]
    settings = load_settings()
    return render_template(
        "home.html",
        recent_history=history_entries,
        favorite_entries=favorite_entries,
        settings=settings,
    )


@main_bp.route("/generate", methods=["POST"])
def generate() -> Response:
    form_data = request.form
    topics_input = form_data.get("topics", "")
    settings = load_settings()
    try:
        depth = int(form_data.get("depth") or settings.get("default_depth", 3))
    except (TypeError, ValueError):
        depth = settings.get("default_depth", 3)
    depth = max(1, min(depth, 6))

    try:
        temperature = float(
            form_data.get("temperature") or settings.get("default_temperature", 0.2)
        )
    except (TypeError, ValueError):
        temperature = settings.get("default_temperature", 0.2)
    temperature = max(0.0, min(temperature, 1.0))
    available_models = current_app.config.get("AVAILABLE_MODELS", [])
    model = form_data.get("model") or settings.get("default_model") or "gpt-3.5-turbo"
    if available_models and model not in available_models:
        model = available_models[0]
    use_demo_mode = bool(form_data.get("demo_mode"))

    topics = _parse_topics(
        topics_input,
        settings.get("default_topics")
        or current_app.config.get("DEFAULT_TOPICS", []),
    )

    generation_request = GenerationRequest(
        topics=topics,
        max_level=depth,
        temperature=temperature,
        model=model,
        use_demo_mode=use_demo_mode,
    )

    try:
        result = generate_topic_tree(
            generation_request,
            api_key=(
                settings.get("api_key")
                or current_app.config.get("OPENAI_API_KEY", "")
            ),
        )
    except SubtopicGenerationError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("main.dashboard"))

    store = get_store()
    result["summary"] = _summarize_trees(result.get("trees", []))
    result["is_favorite"] = False
    store.add_entry(result)

    flash("Subtopics generated successfully!", "success")
    return redirect(url_for("main.view_history_entry", entry_id=result["id"]))


@main_bp.route("/history")
def history() -> str:
    store = get_store()
    query = request.args.get("q", "").strip()
    entries = store.load()
    for entry in entries:
        if entry.get("summary") is None and entry.get("id"):
            summary = _summarize_trees(entry.get("trees", []))
            entry["summary"] = summary
            store.update_entry(entry["id"], {"summary": summary})
    favorites = [entry for entry in entries if entry.get("is_favorite")]
    if query:
        filtered_entries = [
            entry for entry in entries if _entry_matches_query(entry, query)
        ]
    else:
        filtered_entries = entries
    return render_template(
        "history.html",
        entries=filtered_entries,
        favorites=favorites,
        query=query,
        total_count=len(entries),
        filtered_count=len(filtered_entries),
    )


@main_bp.route("/history/<entry_id>")
def view_history_entry(entry_id: str) -> str:
    store = get_store()
    entry = store.get_entry(entry_id)
    if not entry:
        flash("History entry not found.", "warning")
        return redirect(url_for("main.history"))
    summary = entry.get("summary")
    if summary is None:
        summary = _summarize_trees(entry.get("trees", []))
        store.update_entry(entry_id, {"summary": summary})
    return render_template("detail.html", entry=entry, summary=summary)


@main_bp.route("/history/<entry_id>/json")
def download_history_entry(entry_id: str) -> Response:
    store = get_store()
    entry = store.get_entry(entry_id)
    if not entry:
        return jsonify({"error": "Entry not found"}), 404
    return Response(
        response=json.dumps(entry, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={entry_id}.json"},
    )


@main_bp.route("/history/export")
def export_history() -> Response:
    store = get_store()
    entries = store.load()
    return Response(
        response=json.dumps(entries, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=topic-history.json"},
    )


@main_bp.route("/history/<entry_id>/favorite", methods=["POST"])
def toggle_favorite(entry_id: str) -> Response:
    store = get_store()
    entry = store.get_entry(entry_id)
    if not entry:
        flash("History entry not found.", "warning")
        return redirect(url_for("main.history"))

    desired_value = request.form.get("value")
    if desired_value is None:
        new_value = not entry.get("is_favorite", False)
    else:
        new_value = desired_value == "1"

    store.update_entry(entry_id, {"is_favorite": new_value})
    flash(
        "Pinned to favorites" if new_value else "Removed from favorites",
        "success",
    )
    redirect_target = request.form.get("next") or url_for("main.history")
    return redirect(redirect_target)


@main_bp.route("/history/clear", methods=["POST"])
def clear_history() -> Response:
    store = get_store()
    store.clear()
    flash("History cleared.", "info")
    return redirect(url_for("main.history"))


@main_bp.route("/settings", methods=["GET", "POST"])
def settings() -> str:
    store = get_settings_store()
    settings_data = store.load()
    if request.method == "POST":
        form = request.form
        topics = _parse_topics(form.get("default_topics", ""), [])
        api_key_value = form.get("api_key", "").strip()
        payload: Dict[str, object] = {
            "default_model": form.get("default_model", settings_data.get("default_model")),
            "default_depth": form.get("default_depth", settings_data.get("default_depth")),
            "default_temperature": form.get(
                "default_temperature", settings_data.get("default_temperature")
            ),
            "default_demo_mode": bool(form.get("default_demo_mode")),
            "default_topics": topics,
        }
        if form.get("clear_api_key"):
            payload["api_key"] = ""
        elif api_key_value:
            payload["api_key"] = api_key_value
        store.save(payload)
        flash("Settings updated successfully.", "success")
        return redirect(url_for("main.settings"))

    return render_template(
        "settings.html",
        settings=settings_data,
        available_models=current_app.config.get("AVAILABLE_MODELS", []),
        masked_api_key=mask_api_key(settings_data.get("api_key", "")),
    )


def _entry_matches_query(entry: Dict[str, Any], query: str) -> bool:
    lowered = query.casefold()
    for topic in entry.get("topics", []):
        if lowered in topic.casefold():
            return True
    for tree in entry.get("trees", []):
        if _node_contains(tree, lowered):
            return True
    return False


def _node_contains(node: Dict[str, Any], query: str) -> bool:
    if query in str(node.get("topic", "")).casefold():
        return True
    for child in node.get("children", []) or []:
        if _node_contains(child, query):
            return True
    return False


def _summarize_trees(trees: List[Dict[str, Any]]) -> Dict[str, int]:
    summary = {
        "total_nodes": 0,
        "leaf_nodes": 0,
        "max_depth": 0,
    }

    def visit(node: Dict[str, Any], depth: int) -> None:
        summary["total_nodes"] += 1
        summary["max_depth"] = max(summary["max_depth"], depth)
        children = node.get("children", []) or []
        if not children:
            summary["leaf_nodes"] += 1
        for child in children:
            visit(child, depth + 1)

    for tree in trees or []:
        visit(tree, 1)

    return summary
