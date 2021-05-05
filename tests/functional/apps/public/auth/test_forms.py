import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from base.test.factories import UserFactory

from apps.public.auth.forms import PasswordResetForm
from apps.public.auth.forms import UserParametersForm


@pytest.mark.django_db
class TestPasswordResetForm:
    def test_can_properly_choose_standard_users_with_usable_passwords(self):
        user = UserFactory(email="foobar@example.com")
        form = PasswordResetForm({})
        assert list(form.get_users("foobar@example.com")) == [
            user,
        ]

    def test_can_choose_users_without_usable_passwords(self):
        user = UserFactory(email="foobar@example.com")
        user.set_unusable_password()
        user.save()
        form = PasswordResetForm({})
        assert len(list(form.get_users("foobar@example.com")))

    def test_can_properly_send_the_reset_email(self):
        UserFactory(email="foobar@example.com")
        form_data = {
            "email": "foobar@example.com",
        }
        # Run & check
        form = PasswordResetForm(form_data)
        assert form.is_valid()
        form.save(
            domain_override=None,
            subject_template_name="emails/auth/password_reset_subject.txt",
            email_template_name="emails/auth/password_reset_email.html",
            use_https=False,
            token_generator=default_token_generator,
            from_email=None,
            request=None,
            html_email_template_name=None,
        )
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "foobar@example.com"


@pytest.mark.django_db
class TestUserParametersForm:
    def test_cannot_allow_users_to_use_the_email_associated_with_another_user(self):
        # Setup
        u1 = UserFactory.create(username="foo1", email="foo1@erudit.org")
        u2 = UserFactory.create(username="foo2", email="foo2@erudit.org")
        form_data = {
            "username": "foo1",
            "email": u2.email,
        }
        # Run
        form = UserParametersForm(form_data, instance=u1)
        # Check
        assert not form.is_valid()
