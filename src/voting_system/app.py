"""Flask application factory for the localhost prototype."""
from __future__ import annotations
import os
import secrets
from pathlib import Path
from flask import Flask, jsonify
from .auth import bootstrap_admin, register_auth_routes
from .config import Settings\nfrom .roster import register_roster_routes

def _load_or_create_session_secret(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as handle:
            secret = secrets.token_urlsafe(48)
            handle.write(secret)
            handle.flush()
        try:
            path.chmod(0o600)
        except OSError:
            pass
        return secret
    except FileExistsError:
        return path.read_text(encoding="utf-8").strip()

def create_app(test_config: dict[str, object] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATA_ROOT=Path(os.environ.get("VOTING_DATA_ROOT", "instance/data")),
        BOOTSTRAP_ADMIN_EMAIL=os.environ.get("BOOTSTRAP_ADMIN_EMAIL", ""),
        BOOTSTRAP_ADMIN_PASSWORD=os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", ""),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=1_100_000,\n        SESSION_COOKIE_SECURE=False,  # localhost development; enable HTTPS before deployment
    )
    if test_config:
        app.config.update(test_config)
    settings = Settings(Path(app.config["DATA_ROOT"]))
    settings.create_storage_roots()
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = _load_or_create_session_secret(settings.session_secret_file)
    app.extensions["voting_settings"] = settings
    with app.app_context():
        bootstrap_admin(
            str(app.config.get("BOOTSTRAP_ADMIN_EMAIL") or ""),
            str(app.config.get("BOOTSTRAP_ADMIN_PASSWORD") or ""),
        )
    register_auth_routes(app)\n    register_roster_routes(app)

    @app.get("/health")
    def health():
        return jsonify(status="ok", phase="roster_management", crypto_status="pending_protocol_approval"), 200

    @app.get("/")
    def index():
        return jsonify(
            name="Secure Anonymous CR Voting System",
            phase="authentication",
            warning="Academic prototype. Independent administrator/faculty decryption does not provide administrator-resistant privacy.",
        ), 200
    return app
