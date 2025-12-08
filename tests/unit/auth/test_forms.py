"""
Unit tests for authentication form validators.

Tests verify form validation logic including uniqueness checks,
password matching, and required field validation.
"""
from app import db
from app.models import User
from app.auth.forms import (
    RegistrationForm,
    ResetPasswordForm,
    LoginForm,
    ResetPasswordRequestForm
)


def test_registration_form_rejects_duplicate_username(app, client):
    """Test that registration form rejects usernames that already exist."""
    user = User(username="u", email="u@example.com")
    user.set_password("FormTestPass2024!")
    db.session.add(user)
    db.session.commit()

    with client.application.test_request_context():
        form = RegistrationForm()
        form.username.data = "u"
        form.email.data = "u@example.com"
        form.password.data = "FormTestPass2024!"
        form.password2.data = "FormTestPass2024!"

        assert not form.validate()
        assert len(form.username.errors) > 0

        form2 = RegistrationForm()
        form2.username.data = "u2"
        form2.email.data = "u2@example.com"
        form2.password.data = "FormTestPass2024!"
        form2.password2.data = "FormTestPass2024!"
        assert form2.validate()


def test_reset_password_form_validates_password_match(app, client):
    """Test that reset password form validates password confirmation matches."""
    with client.application.test_request_context():
        # Matching passwords should validate
        form = ResetPasswordForm()
        form.password.data = "a"
        form.password2.data = "a"
        assert form.validate()

        # Non-matching passwords should fail validation
        form2 = ResetPasswordForm()
        form2.password.data = "a"
        form2.password2.data = "b"
        assert not form2.validate()


def test_login_form_requires_username_and_password(app, client):
    """Test that login form requires both username and password fields."""
    with client.application.test_request_context():
        form = LoginForm()
        assert not form.validate()


def test_reset_password_request_form_validates_email_format(app, client):
    """Test that reset password request form validates email format."""
    with client.application.test_request_context():
        # Valid email should pass
        form_valid = ResetPasswordRequestForm()
        form_valid.email.data = "user@example.com"
        assert form_valid.validate()

        # Invalid email should fail
        form_invalid = ResetPasswordRequestForm()
        form_invalid.email.data = "not-an-email"
        assert not form_invalid.validate()
