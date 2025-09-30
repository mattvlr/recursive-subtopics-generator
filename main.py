"""WSGI entry point for the Subtopic Explorer Flask application."""

from app import create_app

app = create_app()

if __name__ == "__main__":  # pragma: no cover - manual execution helper
    app.run(debug=True, host="0.0.0.0", port=5000)
