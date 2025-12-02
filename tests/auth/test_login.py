def _login(client, username, password, remember=False, follow_redirects=False):
    return client.post(
        '/auth/login',
        data={
            'username': username,
            'password': password,
            'remember_me': 'y' if remember else '',
            'submit': True,
        },
        follow_redirects=follow_redirects,
    )


def test_login_success_redirects_to_index(client, user_factory):
    user = user_factory(password='Secret123')

    response = _login(client, user.username, 'Secret123')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/index')
    with client.session_transaction() as session:
        assert session.get('_user_id') == str(user.id)


def test_login_invalid_credentials_shows_flash(client, user_factory):
    user = user_factory(password='CorrectPass')

    response = _login(
        client, user.username, 'WrongPass', follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    with client.session_transaction() as session:
        assert session.get('_user_id') is None


def test_login_respects_next_parameter(client, user_factory):
    user = user_factory(password='NextPass')

    response = client.post(
        '/auth/login?next=/messages',
        data={'username': user.username, 'password': 'NextPass', 'submit': True},
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/messages')


def test_login_page_redirects_when_authenticated(client, user_factory):
    user = user_factory(password='AlreadyIn')
    _login(client, user.username, 'AlreadyIn', follow_redirects=False)

    response = client.get('/auth/login')

    assert response.status_code == 302
    assert response.headers['Location'].endswith('/index')

