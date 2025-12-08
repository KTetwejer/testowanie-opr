"""
Integration tests for API token endpoints.

Tests cover token generation via Basic authentication and token revocation.
"""
from base64 import b64encode

from app import db
from app.models import User


def test_generate_token_with_valid_credentials(client):
    """Test that valid Basic auth credentials return a token."""
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
    """Test that requesting a token without credentials returns 401."""
    response = client.post("/api/tokens")
    assert response.status_code == 401


def test_generate_token_with_invalid_credentials_returns_401(client):
    """Test that invalid Basic auth credentials return 401."""
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
    """Test that a valid Bearer token can be revoked successfully."""
    response = client.delete("/api/tokens", headers=auth_headers)
    assert response.status_code == 204


def test_revoke_token_without_authentication_returns_401(client):
    """Test that revoking a token without authentication returns 401."""
    response = client.delete("/api/tokens")
    assert response.status_code == 401


def test_revoke_token_with_invalid_token_returns_401(client):
    """Test that revoking with an invalid token returns 401."""
    response = client.delete(
        "/api/tokens",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
