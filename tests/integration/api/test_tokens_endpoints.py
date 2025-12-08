from base64 import b64encode

from app import db
from app.models import User


def test_generate_token_with_valid_credentials(client):
    user = User(username="u", email="u@example.com")
    user.set_password("ApiUserPass2024!")
    db.session.add(user)
    db.session.commit()

    credentials = b64encode(b"u:ApiUserPass2024!").decode("utf-8")
    response = client.post(
        "/api/tokens",
        headers={"Authorization": f"Basic {credentials}"}
    )
    
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_generate_token_without_credentials_returns_401(client):
    response = client.post("/api/tokens")
    assert response.status_code == 401


def test_generate_token_with_invalid_credentials_returns_401(client):
    user = User(username="u", email="u@example.com")
    user.set_password("ApiUserPass2024!")
    db.session.add(user)
    db.session.commit()

    wrong_credentials = b64encode(b"u:WrongPassword123").decode("utf-8")
    response = client.post(
        "/api/tokens",
        headers={"Authorization": f"Basic {wrong_credentials}"}
    )
    assert response.status_code == 401


def test_revoke_token_with_valid_bearer_token(client, user, auth_headers):
    response = client.delete("/api/tokens", headers=auth_headers)
    assert response.status_code == 204


def test_revoke_token_without_authentication_returns_401(client):
    response = client.delete("/api/tokens")
    assert response.status_code == 401


def test_revoke_token_with_invalid_token_returns_401(client):
    response = client.delete(
        "/api/tokens",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
