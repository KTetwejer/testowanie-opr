import sqlalchemy as sa

from app.models import User


def _register(client, username, email, password='Secret123', follow=False):
    return client.post(
        '/auth/register',
        data={
            'username': username,
            'email': email,
            'password': password,
            'password2': password,
            'submit': True,
        },
        follow_redirects=follow,
    )


def _login(client, username, password):
    return client.post(
        '/auth/login',
        data={'username': username, 'password': password, 'submit': True},
    )


def test_register_success_creates_user_and_redirects(client, db_session):
    response = _register(
        client, username='newuser', email='new@example.com', follow=True
    )

    assert response.status_code == 200
    assert b'Congratulations, you are now a registered user!' in response.data

    user = db_session.scalar(
        sa.select(User).where(User.username == 'newuser')
    )
    assert user is not None
    assert user.email == 'new@example.com'


def test_register_duplicate_username_shows_validation_error(
    client, user_factory
):
    user_factory(username='taken', email='taken@example.com')

    response = _register(
        client,
        username='taken',
        email='other@example.com',
        follow=True,
    )

    assert response.status_code == 200
    assert b'Please use a different username.' in response.data


def test_register_duplicate_email_shows_validation_error(
    client, user_factory
):
    user_factory(username='userA', email='dup@example.com')

    response = _register(
        client,
        username='userB',
        email='dup@example.com',
        follow=True,
    )

    assert response.status_code == 200
    assert b'Please use a different email address.' in response.data


def test_register_redirects_when_authenticated(client, user_factory):
    user = user_factory(password='Secret123')
    _login(client, user.username, 'Secret123')

    response = client.get('/auth/register')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/index')

