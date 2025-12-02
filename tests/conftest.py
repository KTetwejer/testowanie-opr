import os
import pytest

from app import create_app, db
from config import Config
from tests.factories import (
    create_message,
    create_post,
    create_user,
    link_followers,
)


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None
    REDIS_URL = 'redis://'


@pytest.fixture(scope='session')
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.remove()


@pytest.fixture()
def client(app, db_session):
    return app.test_client()


@pytest.fixture()
def runner(app, db_session):
    return app.test_cli_runner()


@pytest.fixture()
def user_factory(db_session):
    def factory(**kwargs):
        return create_user(**kwargs)

    return factory


@pytest.fixture()
def post_factory(db_session):
    def factory(**kwargs):
        return create_post(**kwargs)

    return factory


@pytest.fixture()
def message_factory(db_session):
    def factory(**kwargs):
        return create_message(**kwargs)

    return factory


@pytest.fixture()
def follow_factory(db_session):
    def factory(*pairs, commit=True):
        return link_followers(*pairs, commit=commit)

    return factory

