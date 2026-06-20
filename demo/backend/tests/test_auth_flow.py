from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_valid_login_returns_session() -> None:
    response = client.post(
        "/api/login",
        json={"email": "builder@vibegraph.dev", "password": "ship-fast"},
    )

    assert response.status_code == 200
    assert response.json()["user"] == "builder@vibegraph.dev"


def test_invalid_login_returns_clear_error() -> None:
    response = client.post(
        "/api/login",
        json={"email": "builder@vibegraph.dev", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Email or password is incorrect."}
