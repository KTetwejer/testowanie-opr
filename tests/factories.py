from __future__ import annotations

import itertools
from typing import Tuple

from app import db
from app.models import Message, Post, User

_counter = itertools.count(start=1)


def _next_suffix():
    return next(_counter)


def create_user(
    *,
    username: str | None = None,
    email: str | None = None,
    password: str = 'Password123!',
    commit: bool = True,
    **extra_fields,
) -> User:
    """Return a persisted user with sensible defaults."""
    suffix = _next_suffix()
    user = User(
        username=username or f'user{suffix}',
        email=email or f'user{suffix}@example.com',
        **extra_fields,
    )
    user.set_password(password)
    db.session.add(user)
    _finish(commit)
    return user


def create_post(
    *,
    author: User | None = None,
    body: str | None = None,
    commit: bool = True,
    **extra_fields,
) -> Post:
    """Return a persisted post; author is created if not provided."""
    if author is None:
        author = create_user(commit=False)
    suffix = _next_suffix()
    post = Post(
        body=body or f'Post body {suffix}',
        author=author,
        **extra_fields,
    )
    db.session.add(post)
    _finish(commit)
    return post


def create_message(
    *,
    sender: User | None = None,
    recipient: User | None = None,
    body: str | None = None,
    commit: bool = True,
    **extra_fields,
) -> Message:
    """Return a persisted private message."""
    if sender is None:
        sender = create_user(commit=False)
    if recipient is None:
        recipient = create_user(commit=False)
    suffix = _next_suffix()
    message = Message(
        author=sender,
        recipient=recipient,
        body=body or f'Message body {suffix}',
        **extra_fields,
    )
    db.session.add(message)
    _finish(commit)
    return message


def link_followers(
    *pairs: Tuple[User, User],
    commit: bool = True,
):
    """Create follower relationships between (follower, followed) pairs."""
    for follower, followed in pairs:
        follower.follow(followed)
    _finish(commit)
    return pairs


def _finish(commit: bool) -> None:
    if commit:
        db.session.commit()
    else:
        db.session.flush()

