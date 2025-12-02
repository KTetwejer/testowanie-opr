from datetime import datetime, timezone

import sqlalchemy as sa

from app.models import Message, Notification


def _login(client, username, password):
    return client.post(
        '/auth/login',
        data={'username': username, 'password': password, 'submit': True},
        follow_redirects=True,
    )


def test_send_message_creates_entry_and_notifies(
    client, user_factory, db_session
):
    sender = user_factory(username='alice', password='MsgPass')
    recipient = user_factory(username='bob')

    _login(client, sender.username, 'MsgPass')

    response = client.post(
        f'/send_message/{recipient.username}',
        data={'message': 'Hello Bob!', 'submit': True},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b'Your message has been sent.' in response.data

    message = db_session.scalar(
        sa.select(Message).where(
            Message.author == sender,
            Message.recipient == recipient,
            Message.body == 'Hello Bob!',
        )
    )
    assert message is not None

    notification = db_session.scalar(
        sa.select(Notification).where(
            Notification.user == recipient,
            Notification.name == 'unread_message_count',
        )
    )
    assert notification is not None


def test_messages_list_marks_as_read(client, user_factory, message_factory):
    sender = user_factory(username='alice')
    recipient = user_factory(username='bob', password='MsgPass')

    message_factory(sender=sender, recipient=recipient, body='Hi!')

    _login(client, recipient.username, 'MsgPass')

    response = client.get('/messages')

    assert response.status_code == 200
    assert b'Hi!' in response.data

    assert recipient.last_message_read_time is not None


def test_send_message_requires_login(client):
    response = client.get('/send_message/anyone')

    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

