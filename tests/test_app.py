import string


# ---------- /login ----------

def test_login_success(client):
    resp = client.post("/login", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    resp = client.post("/login", json={"username": "admin", "password": "incorrecta"})
    assert resp.status_code == 401


def test_login_missing_fields(client):
    resp = client.post("/login", json={"username": "admin"})
    assert resp.status_code == 400


def test_login_no_body(client):
    resp = client.post("/login")
    assert resp.status_code == 400


# ---------- /generate-password ----------

def test_generate_password_requires_jwt(client):
    resp = client.get("/generate-password")
    assert resp.status_code == 401


def test_generate_password_default_length(client, auth_header):
    resp = client.get("/generate-password", headers=auth_header)
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["length"] == 12
    assert len(data["password"]) == 12


def test_generate_password_custom_length(client, auth_header):
    resp = client.get("/generate-password?length=32", headers=auth_header)
    assert resp.get_json()["length"] == 32


def test_generate_password_complexity(client, auth_header):
    pwd = client.get("/generate-password?length=20", headers=auth_header).get_json()["password"]
    assert any(c.islower() for c in pwd)
    assert any(c.isupper() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    assert any(c in string.punctuation for c in pwd)


def test_generate_password_respects_flags(client, auth_header):
    resp = client.get(
        "/generate-password?length=20&special_chars=false&numbers=false&uppercase=false",
        headers=auth_header,
    )
    data = resp.get_json()
    assert data["contains_special"] is False
    assert data["contains_numbers"] is False
    assert data["contains_uppercase"] is False
    assert not any(c in string.punctuation for c in data["password"])
    assert not any(c.isdigit() for c in data["password"])
    assert not any(c.isupper() for c in data["password"])


def test_generate_password_length_too_short(client, auth_header):
    resp = client.get("/generate-password?length=4", headers=auth_header)
    assert resp.status_code == 400


def test_generate_password_length_too_long(client, auth_header):
    resp = client.get("/generate-password?length=200", headers=auth_header)
    assert resp.status_code == 400


def test_generate_password_invalid_length(client, auth_header):
    resp = client.get("/generate-password?length=abc", headers=auth_header)
    assert resp.status_code == 400


# ---------- /password-history ----------

def test_password_history_requires_jwt(client):
    resp = client.get("/password-history")
    assert resp.status_code == 401


def test_password_history_records_generated(client, auth_header):
    client.get("/generate-password?length=16", headers=auth_header)
    resp = client.get("/password-history", headers=auth_header)
    data = resp.get_json()
    assert resp.status_code == 200
    assert any(entry["length"] == 16 for entry in data["history"])


# ---------- /check-password-strength ----------

def test_check_password_strength_strong(client, auth_header):
    resp = client.post(
        "/check-password-strength",
        json={"password": "Abcdef123456!"},
        headers=auth_header,
    )
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["strength"] == 5
    assert data["rating"] == "Muy fuerte"


def test_check_password_strength_missing_field(client, auth_header):
    resp = client.post("/check-password-strength", json={}, headers=auth_header)
    assert resp.status_code == 400
