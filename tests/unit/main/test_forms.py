from app import db
from app.models import User
from app.main.forms import EditProfileForm, PostForm, MessageForm


def test_edit_profile_form_rejects_duplicate_username(app, client):
    user = User(username="taken", email="taken@example.com")
    user.set_password("MainFormPass2024!")
    db.session.add(user)
    db.session.commit()

    with client.application.test_request_context():
        # Try to change to existing username should fail
        form = EditProfileForm(original_username="orig")
        form.username.data = "taken"
        assert not form.validate()
        assert len(form.username.errors) > 0

        # Keeping original username should succeed
        form2 = EditProfileForm(original_username="orig")
        form2.username.data = "orig"
        assert form2.validate()


def test_post_form_validates_with_valid_content(app, client):
    with client.application.test_request_context():
        form = PostForm()
        form.post.data = "hello"
        assert form.validate()


def test_message_form_validates_with_valid_message_content(app, client):
    with client.application.test_request_context():
        form = MessageForm()
        form.message.data = "hi"
        assert form.validate()
