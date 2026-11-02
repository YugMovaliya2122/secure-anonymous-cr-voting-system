from io import BytesIO
from pathlib import Path
from voting_system.app import create_app

def _client(tmp_path: Path):
    app = create_app({"TESTING": True, "DATA_ROOT": tmp_path / "data", "SECRET_KEY": "test-secret", "BOOTSTRAP_ADMIN_EMAIL": "admin@example.edu", "BOOTSTRAP_ADMIN_PASSWORD": "a-long-test-password"})
    return app.test_client()

def _csrf(client):
    return client.get("/auth/csrf").json["csrf_token"]

def _login(client, email, password):
    return client.post("/auth/login", json={"email": email, "password": password}, headers={"X-CSRF-Token": _csrf(client)})

def test_admin_imports_roster_and_reads_count(tmp_path: Path):
    client = _client(tmp_path)
    assert _login(client, "admin@example.edu", "a-long-test-password").status_code == 200
    csv_data = b"roll_number,name,email\n23CSB0B21,Student One,student1@example.edu\n23CSB0B22,Student Two,student2@example.edu\n"
    response = client.post("/admin/classes/CSE-2026-B/roster/import", data={"file": (BytesIO(csv_data), "roster.csv")}, headers={"X-CSRF-Token": _csrf(client)}, content_type="multipart/form-data")
    assert response.status_code == 201
    assert response.json["imported_count"] == 2
    assert client.get("/faculty/classes/CSE-2026-B/roster").json["eligible_count"] == 2

def test_roster_import_rejects_duplicate_rolls(tmp_path: Path):
    client = _client(tmp_path)
    assert _login(client, "admin@example.edu", "a-long-test-password").status_code == 200
    csv_data = b"roll_number,name,email\n23CSB0B21,Student One,one@example.edu\n23CSB0B21,Student Two,two@example.edu\n"
    response = client.post("/admin/classes/CSE-2026-B/roster/import", data={"file": (BytesIO(csv_data), "roster.csv")}, headers={"X-CSRF-Token": _csrf(client)}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert "Duplicate roll_number" in response.json["error"]

def test_faculty_cannot_read_other_class_roster(tmp_path: Path):
    client = _client(tmp_path)
    assert _login(client, "admin@example.edu", "a-long-test-password").status_code == 200
    response = client.post("/admin/faculty", json={"email":"faculty@example.edu","password":"another-long-password","display_name":"Faculty","class_id":"CSE-A"}, headers={"X-CSRF-Token":_csrf(client)})
    assert response.status_code == 201
    assert _login(client, "faculty@example.edu", "another-long-password").status_code == 200
    assert client.get("/faculty/classes/CSE-B/roster").status_code == 403
