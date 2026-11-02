"""Tamper-evident administrative audit trail."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any


def append_event(events: list[dict[str, Any]], *, actor_role: str, action: str, details: dict[str, Any]) -> dict[str, Any]:
    previous = events[-1]["event_hash"] if events else "0" * 64
    event = {"timestamp": datetime.now(UTC).isoformat(), "actor_role": actor_role, "action": action, "details": details, "previous_hash": previous}
    material = json.dumps(event, sort_keys=True, separators=(",", ":")).encode("utf-8")
    event["event_hash"] = hashlib.sha256(material).hexdigest()
    events.append(event)
    return event


def verify_chain(events: list[dict[str, Any]]) -> bool:
    prior = "0" * 64
    for event in events:
        copied = dict(event)
        received = copied.pop("event_hash", None)
        material = json.dumps(copied, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if copied.get("previous_hash") != prior or received != hashlib.sha256(material).hexdigest():
            return False
        prior = received
    return True
