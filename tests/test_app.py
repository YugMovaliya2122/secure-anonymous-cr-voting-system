from pathlib import Path

from voting_system.app import create_app


def test_health_reports_crypto_gate(tmp_path: Path) -> None:
    app = create_app({"TESTING": True, "DATA_ROOT": tmp_path / "data"})
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json["crypto_status"] == "pending_protocol_approval"
