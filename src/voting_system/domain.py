"""Domain types shared by non-cryptographic modules."""

from enum import StrEnum


class Role(StrEnum):
    MAIN_ADMIN = "main_admin"
    FACULTY_OFFICER = "faculty_officer"
    CANDIDATE = "candidate"
    VOTER = "voter"


class ElectionState(StrEnum):
    DRAFT = "draft"
    APPLICATIONS_OPEN = "applications_open"
    CONFIGURED = "configured"
    OPEN = "open"
    CLOSED = "closed"
    TALLIED = "tallied"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
