import json

from app import db
from app.models import User


def test_create_user_successfully(client):
    payload = {
        "username": "u1",
        "email": "u1@example.com",
        "password": "NewApiUser2024!"
    }
    response = client.post(
        "/api/users",
        data=json.dumps(payload),
        content_type="application/json"
    )
    
    assert response.status_code == 201
    response_data = response.get_json()
    user = db.session.get(User, response_data["id"])
    
    assert user.username == "u1"
    assert user.email == "u1@example.com"
    assert user.check_password("NewApiUser2024!")


def test_get_users_list_requires_authentication(client):
    response = client.get("/api/users")
    assert response.status_code == 401


def test_get_users_list_with_authentication(client, auth_headers):
    response = client.get("/api/users", headers=auth_headers)
    assert response.status_code == 200
    assert "items" in response.get_json()


def test_create_user_with_duplicate_username_returns_400(client):
    payload = {
        "username": "u1",
        "email": "u1@example.com",
        "password": "NewApiUser2024!"
    }

    response1 = client.post(
        "/api/users",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response1.status_code == 201
    assert response1.get_json()["username"] == "u1"

    response2 = client.post(
        "/api/users",
        data=json.dumps(payload),
        content_type="application/json"
    )
    assert response2.status_code == 400


def test_create_user_with_duplicate_email_returns_400(client):
    payload1 = {
        "username": "u1",
        "email": "u1@example.com",
        "password": "NewApiUser2024!"
    }
    client.post(
        "/api/users",
        data=json.dumps(payload1),
        content_type="application/json"
    )

    payload2 = {
        "username": "u2",
        "email": "u1@example.com",
        "password": "AnotherPass2024@"
    }
    response = client.post(
        "/api/users",
        data=json.dumps(payload2),
        content_type="application/json"
    )
    assert response.status_code == 400


def test_get_user_requires_authentication(client, user):
    response = client.get(f"/api/users/{user.id}")
    assert response.status_code == 401


def test_get_user_with_valid_token_returns_user_data(client, user, auth_headers):
    response = client.get(f"/api/users/{user.id}", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.get_json()["username"] == user.username


def test_get_followers_returns_empty_list_for_new_user(client, user, auth_headers):
    user2 = User(username="testuser2", email="testuser2@example.com")
    user2.set_password("SecondUserPass2024!")
    db.session.add(user2)
    db.session.commit()

    response = client.get(
        f"/api/users/{user.id}/followers",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_get_following_returns_empty_list_for_new_user(client, user, auth_headers):
    user2 = User(username="testuser2", email="testuser2@example.com")
    user2.set_password("SecondUserPass2024!")
    db.session.add(user2)
    db.session.commit()

    response = client.get(
        f"/api/users/{user.id}/following",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.get_json()["items"] == []


def test_update_own_user_profile_succeeds(client, user, auth_headers):
    update_data = {
        "username": "new",
        "email": "n@example.com"
    }
    response = client.put(
        f"/api/users/{user.id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers,
    )
    
    assert response.status_code == 200
    user_updated = db.session.get(User, user.id)
    assert user_updated.username == "new"
    assert user_updated.email == "n@example.com"


def test_update_user_with_duplicate_username_returns_400(client, user, auth_headers):
    user2 = User(username="testuser2", email="testuser2@example.com")
    user2.set_password("SecondUserPass2024!")
    db.session.add(user2)
    db.session.commit()

    update_data = {"username": "testuser2"}
    response = client.put(
        f"/api/users/{user.id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_update_other_user_profile_returns_403(client, user, auth_headers):
    user2 = User(username="testuser2", email="testuser2@example.com")
    user2.set_password("SecondUserPass2024!")
    db.session.add(user2)
    db.session.commit()
    token2 = user2.get_token()
    db.session.commit()
    auth_headers2 = {"Authorization": f"Bearer {token2}"}

    update_data = {"username": "new", "email": "n@example.com"}
    response = client.put(
        f"/api/users/{user.id}",
        data=json.dumps(update_data),
        content_type="application/json",
        headers=auth_headers2,
    )
    assert response.status_code == 403
