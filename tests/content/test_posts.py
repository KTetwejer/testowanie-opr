import sqlalchemy as sa

from app.models import Post


def _login(client, username, password, follow=True):
    response = client.post(
        '/auth/login',
        data={'username': username, 'password': password, 'submit': True},
        follow_redirects=follow,
    )
    return response


def test_index_requires_login(client):
    response = client.get('/index')

    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']


def test_post_submission_creates_post(
    client, user_factory, db_session, monkeypatch
):
    user = user_factory(password='PostPass')
    _login(client, user.username, 'PostPass')
    monkeypatch.setattr('app.main.routes.detect', lambda _: 'en')

    response = client.post(
        '/index',
        data={'post': 'Hello world', 'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Your post is now live!' in response.data

    post = db_session.scalar(
        sa.select(Post).where(Post.author == user, Post.body == 'Hello world')
    )
    assert post is not None
    assert post.language == 'en'


def test_feed_shows_followed_posts(
    client, user_factory, post_factory, follow_factory
):
    user = user_factory(username='reader', password='FeedPass')
    followed_user = user_factory(username='followed')
    unfollowed_user = user_factory(username='stranger')

    follow_factory((user, followed_user))

    post_followed = post_factory(author=followed_user, body='Followed post!')
    post_factory(author=unfollowed_user, body='Hidden post!')

    _login(client, user.username, 'FeedPass')

    response = client.get('/index')

    assert response.status_code == 200
    assert b'Followed post!' in response.data
    assert b'Hidden post!' not in response.data

