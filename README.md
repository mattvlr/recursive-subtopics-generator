# Subtopic Explorer

Subtopic Explorer is a Flask web application that turns the original recursive subtopic generator script into an interactive tool. Enter one or more high-level topics and the app will build a nested tree of subtopics using OpenAI's chat completions. A history view keeps track of every generation and lets you download the JSON payload for further analysis. When you do not have an API key configured, the site runs in a deterministic demo mode so you can preview the experience locally.

## Features

- Web UI for generating one or more subtopic trees with adjustable recursion depth, temperature, and OpenAI model.
- Demo mode that synthesizes predictable sample subtopics when no API key is available.
- Workspace settings page to securely store your OpenAI API key, set default generation options, and curate starter topics.
- Persistent history with favorites, search, pinned insights, and one-click exports (per-entry or full archive).
- Interactive tree viewer with collapsible nodes, automatic node statistics, and quick topic chips for inspiration.
- Local Bootstrap assets are bundled so the UI stays fully styled even without CDN access.

## Getting started

### Prerequisites

- Python 3.10+
- A valid OpenAI API key (optional for demo mode)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set your API key in one of three ways:

1. Open the in-app **Settings** page (recommended) and paste your key into the OpenAI connection form.
2. Edit `config.py` and set `API_KEY`.
3. Export an environment variable before starting the server:

```bash
export OPENAI_API_KEY="sk-your-key"
```

### Running the development server

```bash
flask --app main run --debug
```

The app will start on [http://localhost:5000](http://localhost:5000). Use the form on the home page to enter top-level topics and generate your topic maps. Visit the history page to search, pin favorites, clear runs, or export JSON. The settings page persists its configuration in `instance/settings.json` so tweaks survive restarts.

## Project structure

- `app/__init__.py` – Flask application factory and configuration helpers.
- `app/routes.py` – HTTP routes and controller logic.
- `app/services/subtopics.py` – Recursive generator that calls OpenAI or demo mode.
- `app/storage.py` – Simple JSON-backed history store.
- `app/settings.py` – JSON-backed workspace configuration helpers.
- `app/templates/` – Jinja templates for the UI.
- `app/static/` – Stylesheets, JavaScript bundles, and other static assets for the interface.
- `main.py` – WSGI entry point for running the Flask app.

## License

This project is licensed under the [MIT License](LICENSE).
