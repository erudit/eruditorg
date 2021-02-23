# -*- coding: utf-8 -*-

import pytest
import os.path as op

from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings

from core.email.email import Email


@override_settings(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": ["%s/templates" % op.abspath(op.dirname(__file__))],
            "OPTIONS": {
                "context_processors": [
                    "django.core.context_processors.request",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.template.context_processors.static",
                ],
            },
        },
    ]
)
@pytest.mark.django_db
class TestEmail(TestCase):
    def test_can_send_a_simple_email_by_generating_the_text_content(self):
        # Setup
        email = Email("dummy@dummy.com", html_template="mail_dummy.html", subject="Subject")
        # Run
        email.send()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "dummy@dummy.com"
        assert mail.outbox[0].subject == "Subject"
        assert mail.outbox[0].body.strip() == "Hello"
        assert len(mail.outbox[0].alternatives) == 1
        assert mail.outbox[0].alternatives[0][0].strip() == "<p>Hello</p>"
        assert mail.outbox[0].alternatives[0][1] == "text/html"

    def test_can_send_a_simple_email_with_a_text_template(self):
        # Setup
        email = Email(
            "dummy@dummy.com",
            html_template="mail_dummy.html",
            text_template="mail_dummy.txt",
            subject="Subject",
        )
        # Run
        email.send()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "dummy@dummy.com"
        assert mail.outbox[0].subject == "Subject"
        assert mail.outbox[0].body.strip() == "Hello txt"
        assert len(mail.outbox[0].alternatives) == 1
        assert mail.outbox[0].alternatives[0][0].strip() == "<p>Hello</p>"
        assert mail.outbox[0].alternatives[0][1] == "text/html"

    def test_can_send_a_simple_email_with_a_subject_template(self):
        # Setup
        email = Email(
            "dummy@dummy.com", html_template="mail_dummy.html", subject_template="mail_subject.html"
        )
        # Run
        email.send()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to[0] == "dummy@dummy.com"
        assert mail.outbox[0].subject == "Hello subject"
        assert mail.outbox[0].body.strip() == "Hello"
        assert len(mail.outbox[0].alternatives) == 1
        assert mail.outbox[0].alternatives[0][0].strip() == "<p>Hello</p>"
        assert mail.outbox[0].alternatives[0][1] == "text/html"

    def test_can_use_an_extra_context(self):
        # Setup
        email = Email(
            "dummy@dummy.com",
            html_template="mail_extra_context.html",
            subject="Subject",
            extra_context={"foo": "bar"},
        )
        # Run
        email.send()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].body.strip() == "bar"

    def test_can_be_sent_in_a_specific_language(self):
        # Setup
        email = Email(
            "dummy@dummy.com",
            html_template="mail_language.html",
            subject="Subject",
            extra_context={"foo": "bar"},
            language="en",
        )
        # Run
        email.send()
        # Check
        assert len(mail.outbox) == 1
        assert mail.outbox[0].body.strip() == "en"

    def test_email_tag_will_be_converted_to_mailgun_header(self):
        email = Email(
            "dummy@dummy.com", html_template="mail_dummy.html", subject="Subject", tag="test"
        )
        # Run
        email.send()
        # Check
        test_email = mail.outbox[0]
        assert "X-Mailgun-Tag" in test_email.extra_headers
        assert test_email.extra_headers["X-Mailgun-Tag"] == "test"
