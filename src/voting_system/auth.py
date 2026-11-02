"""Local identity and session authentication.

Identity records are stored separately from ballot records. Passwords are stored
as Werkzeug scrypt hashes, never as plaintext.
"""
from __future__ import annotations
import hmac
import secrets
import uuid
from functools import wraps
from typing import Any, Callable
from flask import current_app, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from .domain import Role
from .storage import AtomicJsonStore

def _users() -> AtomicJsonStore:
    return AtomicJsonStore(current_app.extensions["voting_settings"].users_file)

def normalize_email(value: Any) -> str:
    return value.strip().casefold() if isinstance(value, str) else ""

def _valid_password(value: Any) -> bool:
    return isinstance(value, str) and 12 <= len(value) <= 256

def create_user(*, email: str, password: str, role: Role, display_name: str, class_id: str | None = None) -> dict[str, Any]:
    normalized_email = normalize_email(email)
    if not normalized_email or "@" not in normalized_email or len(normalized_email) > 254:
        raise ValueError("A valid email address is required.")
    if not _valid_password(password):
        raise ValueError("Password must contain between 12 and 256 characters.")
    if not isinstance(display_name, str) or not display_name.strip() or len(display_name) > 100:
        raise ValueError("A display name of 1 to 100 characters is required.")
    return {
        "user_id": str(uuid.uuid4()),
        "email": normalized_email,
        "password_hash": generate_password_hash(password, method="scrypt"),
        "role": role.value,
        "display_name": display_name.strip(),
        "class_id": class_id,
        "active": True,
    }

def bootstrap_admin(email: str, password: str) -> bool:
    if not email or not password:
        return False
    admin = create_user(email=email, password=password, role=Role.MAIN_ADMIN, display_name="Main Administrator")
    created = False
    def add_if_empty(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
        nonlocal created
        if users:
            return users
        created = True
        return [admin]
    _users().transact([], add_if_empty)
    return created

def find_user_by_id(user_id: str) -> dict[str, Any] | None:
    return next((u for u in _users().read([]) if u.get("user_id") == user_id), None)

def find_user_by_email(email: str) -> dict[str, Any] | None:
    normalized = normalize_email(email)
    return next((u for u in _users().read([]) if u.get("email") == normalized), None)

def csrf_token() -> str:
    token = session.get("csrf_token")
    if not isinstance(token, str):
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token

def require_csrf() -> bool:
    expected = session.get("csrf_token")
    supplied = request.headers.get("X-CSRF-Token", "")
    return isinstance(expected, str) and bool(supplied) and hmac.compare_digest(expected, supplied)

def require_roles(*roles: Role) -> Callable:
    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any):
            user_id = session.get("user_id")
            user = find_user_by_id(user_id) if isinstance(user_id, str) else None
            if not user or not user.get("active", False):
                return jsonify(error="authentication_required"), 401
            if user.get("role") not in {role.value for role in roles}:
                return jsonify(error="forbidden"), 403
            request.environ["voting.current_user"] = user
            return view(*args, **kwargs)
        return wrapped
    return decorator

def register_auth_routes(app) -> None:
    @app.get("/auth/csrf")
    def get_csrf():
        return jsonify(csrf_token=csrf_token())

    @app.post("/auth/login")
    def login():
        if not require_csrf():
            return jsonify(error="csrf_validation_failed"), 400
        payload = request.get_json(silent=True) or {}
        user = find_user_by_email(payload.get("email"))
        password = payload.get("password")
        if not user or not user.get("active", False) or not isinstance(password, str) or not check_password_hash(user["password_hash"], password):
            return jsonify(error="invalid_email_or_password"), 401
        session.clear()
        session["user_id"] = user["user_id"]
        session["csrf_token"] = secrets.token_urlsafe(32)
        return jsonify(user={"email": user["email"], "role": user["role"], "display_name": user["display_name"], "class_id": user.get("class_id")}, csrf_token=session["csrf_token"]), 200

    @app.post("/auth/logout")
    def logout():
        if not require_csrf():
            return jsonify(error="csrf_validation_failed"), 400
        session.clear()
        return jsonify(status="logged_out"), 200

    @app.get("/auth/me")
    def me():
        user_id = session.get("user_id")
        user = find_user_by_id(user_id) if isinstance(user_id, str) else None
        if not user or not user.get("active", False):
            return jsonify(error="authentication_required"), 401
        return jsonify(user={"email": user["email"], "role": user["role"], "display_name": user["display_name"], "class_id": user.get("class_id")}), 200

    @app.post("/admin/faculty")
    @require_roles(Role.MAIN_ADMIN)
    def create_faculty():
        if not require_csrf():
            return jsonify(error="csrf_validation_failed"), 400
        payload = request.get_json(silent=True) or {}
        class_id = payload.get("class_id")
        if not isinstance(class_id, str) or not class_id.strip() or len(class_id) > 100:
            return jsonify(error="valid_class_id_required"), 400
        try:
            faculty = create_user(email=payload.get("email"), password=payload.get("password"), role=Role.FACULTY_OFFICER, display_name=payload.get("display_name"), class_id=class_id.strip())
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        created = False
        def add_user(users: list[dict[str, Any]]) -> list[dict[str, Any]]:
            nonlocal created
            if any(u.get("email") == faculty["email"] for u in users):
                return users
            created = True
            return [*users, faculty]
        _users().transact([], add_user)
        if not created:
            return jsonify(error="email_already_registered"), 409
        return jsonify(user={"email": faculty["email"], "role": faculty["role"], "display_name": faculty["display_name"], "class_id": faculty["class_id"]}), 201
