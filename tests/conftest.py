"""
Pytest configuration and shared fixtures for integration and unit tests.

This module provides test fixtures and helper functions used across
all test suites. It sets up a clean test environment with an in-memory
database and provides utilities for authentication and user management.
"""
import pytest

from app import create_app, db
from app.models import User
from config import Config


class TestConfig(Config):
    """Test configuration overriding production settings."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    TESTING = True


@pytest.fixture(scope="session")
def app():
    """Create and configure Flask application for testing."""
    app = create_app(TestConfig)
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """
    Create a test client for making HTTP requests.
    
    Sets up a fresh database for each test and cleans up afterwards.
    """
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user(client):
    """
    Create a test user for authentication tests.
    
    Returns:
        User: A user instance with username 'testuser' and password 'TestPass2024!'
    """
    user = User(username="testuser", email="testuser@example.com")
    user.set_password("TestPass2024!")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_headers(user: User):
    """
    Generate authentication headers with Bearer token.
    
    Args:
        user: User instance to generate token for
        
    Returns:
        dict: Headers dictionary with Authorization Bearer token
    """
    token = user.get_token()
    db.session.commit()
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def second_user(client):
    """Create a second test user for testing interactions between users."""
    user = User(username="otheruser", email="otheruser@example.com")
    user.set_password("OtherUserPass2024!")
    db.session.add(user)
    db.session.commit()
    return user


def login_user_via_client(client, username, password):
    """
    Helper function to log in a user via test client.
    
    Args:
        client: Flask test client
        username: Username to log in with
        password: Password to log in with
        
    Returns:
        Response: Flask response object from login request
    """
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=False,
    )


def is_logged_in(client):
    """
    Check if a user is currently logged in via test client.
    
    Args:
        client: Flask test client
        
    Returns:
        bool: True if user is logged in, False otherwise
    """
    return ("Sign In" and "Redirecting...") not in client.get("/index").get_data(
        as_text=True
    )


def create_test_user(username="testuser", email="testuser@example.com", password="TestPass2024!"):
    """
    Helper function to create a test user in the database.
    
    Args:
        username: Username for the new user
        email: Email for the new user
        password: Password for the new user
        
    Returns:
        User: Created user instance
    """
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
