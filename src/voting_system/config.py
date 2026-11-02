"""Filesystem layout for the localhost prototype."""
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    data_root: Path
    @property
    def identity_root(self) -> Path: return self.data_root / "identity"
    @property
    def ballot_root(self) -> Path: return self.data_root / "ballot_box"
    @property
    def audit_root(self) -> Path: return self.data_root / "audit"
    @property
    def roster_root(self) -> Path: return self.identity_root / "rosters"
    @property
    def users_file(self) -> Path: return self.identity_root / "users.json"
    @property
    def session_secret_file(self) -> Path: return self.data_root / ".session-secret"
    def create_storage_roots(self) -> None:
        for root in (self.identity_root, self.ballot_root, self.audit_root, self.roster_root):
            root.mkdir(parents=True, exist_ok=True)
