"""End-to-end tests covering authentication and RBAC enforcement."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def login(username: str, password: str) -> str:
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_health():
    assert client.get("/").json()["status"] == "ok"


def test_login_success_and_me():
    token = login("alice", "alice12345")
    resp = client.get("/users/me", headers=auth_header(token))
    assert resp.status_code == 200
    assert resp.json() == {"username": "alice", "role": "user"}


def test_login_wrong_password():
    resp = client.post(
        "/auth/login", data={"username": "alice", "password": "wrongpass123"}
    )
    assert resp.status_code == 401


def test_protected_endpoint_requires_token():
    assert client.get("/users/me").status_code == 401


def test_tampered_token_rejected():
    token = login("alice", "alice12345")
    resp = client.get("/users/me", headers=auth_header(token + "x"))
    assert resp.status_code == 401


def test_user_cannot_access_admin_endpoint():
    token = login("alice", "alice12345")
    resp = client.get("/users", headers=auth_header(token))
    assert resp.status_code == 403  # authenticated but not authorized


def test_admin_can_list_users():
    token = login("admin", "admin12345")
    resp = client.get("/users", headers=auth_header(token))
    assert resp.status_code == 200
    usernames = {u["username"] for u in resp.json()}
    assert {"admin", "alice"}.issubset(usernames)


def test_register_then_login():
    client.post(
        "/auth/register",
        json={"username": "bob", "password": "bobpass12345", "role": "user"},
    )
    token = login("bob", "bobpass12345")
    assert client.get("/users/me", headers=auth_header(token)).status_code == 200


def test_register_duplicate_rejected():
    resp = client.post(
        "/auth/register",
        json={"username": "alice", "password": "whatever12345", "role": "user"},
    )
    assert resp.status_code == 409


def test_admin_can_delete_user_but_not_self():
    token = login("admin", "admin12345")
    client.post(
        "/auth/register",
        json={"username": "tempuser", "password": "temppass12345", "role": "user"},
    )
    assert client.delete("/users/tempuser", headers=auth_header(token)).status_code == 204
    assert client.delete("/users/admin", headers=auth_header(token)).status_code == 400
