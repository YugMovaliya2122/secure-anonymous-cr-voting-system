"""Flask application factory for the phase-one foundation."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify

from .config import Settings


def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(DATA_ROOT=Path("instance/data"))
    if test_config:
        app.config.update(test_config)
    settings = Settings(Path(app.config["DATA_ROOT"]))
    settings.create_storage_roots()
    app.extensions["voting_settings"] = settings

    @app.get("/health")
    def health() -> tuple[object, int]:
        return jsonify(status="ok", phase="foundation", crypto_status="pending_protocol_approval"), 200

    @app.get("/")
    def index() -> tuple[object, int]:
        return jsonify(name="Secure Anonymous CR Voting System", warning="Academic prototype. Dual-recipient decryption is not administrator-resistant."), 200

    return app
