"""Roll-number validation and class grouping for the college roster.

The institution's roll format is YYCCBBSNN: the first seven characters
(YYCCBBS) identify one class. Example: 23CSB0B21 belongs to class 23CSB0B.
"""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

ROLL_NUMBER_PATTERN = re.compile(r"^(?P<year>\d{2})(?P<branch>[A-Z]{2})(?P<program>B[0-9])(?P<section>[A-Z])(?P<serial>\d{2})$", re.IGNORECASE)


def normalize_roll_number(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Roll number must be text.")
    normalized = value.strip().upper()
    if not ROLL_NUMBER_PATTERN.fullmatch(normalized):
        raise ValueError("Roll number must match the college format, for example 23CSB0B21.")
    return normalized


def class_id_from_roll_number(value: Any) -> str:
    """Return the seven-character class key from a valid roll number."""
    return normalize_roll_number(value)[:7]


def group_roster_by_class(students: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Validate and group roster rows by roll number class prefix."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    seen: set[str] = set()
    for row in students:
        roll = normalize_roll_number(row.get("roll_number"))
        if roll in seen:
            raise ValueError(f"Duplicate roll number: {roll}")
        seen.add(roll)
        groups[class_id_from_roll_number(roll)].append({**row, "roll_number": roll, "class_id": roll[:7]})
    return dict(groups)
