import app.main.routes as main_routes


def _login(client, username, password):
    return client.post(
        '/auth/login',
        data={'username': username, 'password': password, 'submit': True},
        follow_redirects=True,
    )


def test_follow_user_success(client, user_factory):
    follower = user_factory(username='alice', password='FollowPass')
    followed = user_factory(username='bob')

    _login(client, follower.username, 'FollowPass')

    response = client.post(
        f'/follow/{followed.username}',
        data={'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'You are following' in response.data
    assert follower.is_following(followed)


def test_follow_requires_form_validation(client, user_factory, monkeypatch):
    follower = user_factory(username='alice', password='FollowPass')
    followed = user_factory(username='bob')

    _login(client, follower.username, 'FollowPass')

    monkeypatch.setattr(
        main_routes.EmptyForm, 'validate_on_submit', lambda self: False
    )

    response = client.post(
        f'/follow/{followed.username}', data={'submit': True}, follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Home' in response.data  # redirected to index template
    assert not follower.is_following(followed)


def test_follow_self_shows_error(client, user_factory):
    user = user_factory(username='selfie', password='FollowPass')

    _login(client, user.username, 'FollowPass')

    response = client.post(
        f'/follow/{user.username}',
        data={'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'You cannot follow yourself!' in response.data


def test_follow_nonexistent_user_flash(client, user_factory):
    follower = user_factory(username='alice', password='FollowPass')

    _login(client, follower.username, 'FollowPass')

    response = client.post(
        '/follow/missing-user',
        data={'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'User missing-user not found.' in response.data


def test_unfollow_user_success(client, user_factory, follow_factory):
    follower = user_factory(username='alice', password='FollowPass')
    followed = user_factory(username='bob')
    follow_factory((follower, followed))

    _login(client, follower.username, 'FollowPass')

    response = client.post(
        f'/unfollow/{followed.username}',
        data={'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'You are not following' in response.data
    assert not follower.is_following(followed)

