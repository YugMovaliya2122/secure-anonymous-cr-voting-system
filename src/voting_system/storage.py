"""Locked, atomically persisted JSON state.

This module is for identity and administrative records only. Ballot records
must be stored in a dedicated ballot-box module and must never contain an
identity identifier.
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

import portalocker

T = TypeVar("T")


class AtomicJsonStore:
    """Serialize read-modify-write transitions with a sibling lock file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock_path = path.with_suffix(path.suffix + ".lock")

    def read(self, default: T) -> T:
        if not self.path.exists():
            return default
        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def transact(self, default: T, update: Callable[[T], T]) -> T:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with portalocker.Lock(str(self.lock_path), mode="a+", timeout=5):
            current = self.read(default)
            next_value = update(current)
            self._atomic_write(next_value)
            return next_value

    def _atomic_write(self, value: Any) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(value, handle, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, self.path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
