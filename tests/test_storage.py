from pathlib import Path

from voting_system.storage import AtomicJsonStore


def test_transaction_persists_json_atomically(tmp_path: Path) -> None:
    store = AtomicJsonStore(tmp_path / "identity" / "roster.json")
    outcome = store.transact([], lambda current: [*current, {"student_id": "S001"}])
    assert outcome == [{"student_id": "S001"}]
    assert store.read([]) == outcome
