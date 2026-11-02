"""Official class roster import and lookup.

Roster records are identity data and are never written to the ballot box.
CSV import is intentionally restricted to the Main Admin.
"""
from __future__ import annotations
import csv
import io
import re
from typing import Any
from flask import current_app, jsonify, request
from .auth import require_csrf, require_roles
from .domain import Role
from .storage import AtomicJsonStore

MAX_ROSTER_BYTES = 1_000_000
MAX_ROSTER_ROWS = 5_000
REQUIRED_COLUMNS = {"roll_number", "name", "email"}
ROLL_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,39}$")

def _roster_store(class_id: str) -> AtomicJsonStore:
    settings = current_app.extensions["voting_settings"]
    # class_id is validated before it reaches this function; keep path safe regardless.
    safe_id = re.sub(r"[^A-Za-z0-9._-]", "_", class_id)[:100]
    return AtomicJsonStore(settings.roster_root / f"{safe_id}.json")

def _parse_roster_csv(raw: bytes) -> list[dict[str, str]]:
    if len(raw) > MAX_ROSTER_BYTES:
        raise ValueError("CSV file exceeds the 1 MB limit.")
    try:
        decoded = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8 encoded.") from exc
    reader = csv.DictReader(io.StringIO(decoded))
    if not reader.fieldnames:
        raise ValueError("CSV must contain a header row.")
    headers = {h.strip().casefold() for h in reader.fieldnames if h}
    if not REQUIRED_COLUMNS.issubset(headers):
        raise ValueError("CSV headers must include roll_number, name, and email.")
    # Map case/whitespace variants back to canonical keys.
    original = {h.strip().casefold(): h for h in reader.fieldnames if h}
    records: list[dict[str, str]] = []
    seen_rolls: set[str] = set()
    seen_emails: set[str] = set()
    for line_number, row in enumerate(reader, start=2):
        if len(records) >= MAX_ROSTER_ROWS:
            raise ValueError(f"Roster cannot exceed {MAX_ROSTER_ROWS} students.")
        roll = (row.get(original["roll_number"]) or "").strip().upper()
        name = (row.get(original["name"]) or "").strip()
        email = (row.get(original["email"]) or "").strip().casefold()
        if not roll or not ROLL_RE.fullmatch(roll):
            raise ValueError(f"Invalid roll_number on CSV line {line_number}.")
        if not name or len(name) > 120:
            raise ValueError(f"Invalid name on CSV line {line_number}.")
        if not email or len(email) > 254 or email.count("@") != 1 or any(c.isspace() for c in email):
            raise ValueError(f"Invalid email on CSV line {line_number}.")
        if roll in seen_rolls:
            raise ValueError(f"Duplicate roll_number on CSV line {line_number}.")
        if email in seen_emails:
            raise ValueError(f"Duplicate email on CSV line {line_number}.")
        seen_rolls.add(roll)
        seen_emails.add(email)
        records.append({"roll_number": roll, "name": name, "email": email, "eligible": True})
    if not records:
        raise ValueError("CSV contains no student records.")
    return records

def register_roster_routes(app) -> None:
    @app.post("/admin/classes/<class_id>/roster/import")
    @require_roles(Role.MAIN_ADMIN)
    def import_roster(class_id: str):
        if not require_csrf():
            return jsonify(error="csrf_validation_failed"), 400
        if not class_id or len(class_id) > 100 or not re.fullmatch(r"[A-Za-z0-9._-]+", class_id):
            return jsonify(error="invalid_class_id"), 400
        upload = request.files.get("file")
        if upload is None:
            return jsonify(error="csv_file_required"), 400
        try:
            records = _parse_roster_csv(upload.read(MAX_ROSTER_BYTES + 1))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        store = _roster_store(class_id)
        # Replacing a roster is a deliberate admin action; preserve no historical identity links.
        store.transact([], lambda _current: records)
        return jsonify(class_id=class_id, imported_count=len(records), status="roster_imported"), 201

    @app.get("/faculty/classes/<class_id>/roster")
    @require_roles(Role.MAIN_ADMIN, Role.FACULTY_OFFICER)
    def get_roster_summary(class_id: str):
        if not class_id or len(class_id) > 100 or not re.fullmatch(r"[A-Za-z0-9._-]+", class_id):
            return jsonify(error="invalid_class_id"), 400
        actor: dict[str, Any] = request.environ["voting.current_user"]
        if actor["role"] == Role.FACULTY_OFFICER.value and actor.get("class_id") != class_id:
            return jsonify(error="forbidden"), 403
        records = _roster_store(class_id).read([])
        return jsonify(class_id=class_id, eligible_count=len(records)), 200
