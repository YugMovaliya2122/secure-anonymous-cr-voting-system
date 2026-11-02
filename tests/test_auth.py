from pathlib import Path
from voting_system.app import create_app

def _csrf(client) -> str:
    response = client.get("/auth/csrf")
    assert response.status_code == 200
    return response.json["csrf_token"]

def _login(client, email: str, password: str):
    return client.post("/auth/login", json={"email": email, "password": password}, headers={"X-CSRF-Token": _csrf(client)})

def test_bootstrap_admin_can_login_and_view_session(tmp_path: Path) -> None:
    app = create_app({"TESTING": True, "DATA_ROOT": tmp_path / "data", "SECRET_KEY": "test-secret", "BOOTSTRAP_ADMIN_EMAIL": "admin@example.edu", "BOOTSTRAP_ADMIN_PASSWORD": "a-long-test-password"})
    client = app.test_client()
    response = _login(client, "ADMIN@example.edu", "a-long-test-password")
    assert response.status_code == 200
    assert response.json["user"]["role"] == "main_admin"
    assert client.get("/auth/me").json["user"]["email"] == "admin@example.edu"

def test_admin_can_create_class_scoped_faculty(tmp_path: Path) -> None:
    app = create_app({"TESTING": True, "DATA_ROOT": tmp_path / "data", "SECRET_KEY": "test-secret", "BOOTSTRAP_ADMIN_EMAIL": "admin@example.edu", "BOOTSTRAP_ADMIN_PASSWORD": "a-long-test-password"})
    client = app.test_client()
    assert _login(client, "admin@example.edu", "a-long-test-password").status_code == 200
    response = client.post("/admin/faculty", json={"email": "faculty@example.edu", "password": "another-long-password", "display_name": "Faculty Officer", "class_id": "CSE-2026-B"}, headers={"X-CSRF-Token": _csrf(client)})
    assert response.status_code == 201
    assert response.json["user"]["class_id"] == "CSE-2026-B"
    assert response.json["user"]["role"] == "faculty_officer"

def test_login_requires_csrf_and_bad_password_fails(tmp_path: Path) -> None:
    app = create_app({"TESTING": True, "DATA_ROOT": tmp_path / "data", "SECRET_KEY": "test-secret", "BOOTSTRAP_ADMIN_EMAIL": "admin@example.edu", "BOOTSTRAP_ADMIN_PASSWORD": "a-long-test-password"})
    client = app.test_client()
    assert client.post("/auth/login", json={"email": "admin@example.edu", "password": "a-long-test-password"}).status_code == 400
    assert _login(client, "admin@example.edu", "wrong-password").status_code == 401
