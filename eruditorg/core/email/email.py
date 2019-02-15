# -*- coding: utf-8 -*-

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import force_text
import html2text
from post_office import mail

from base.context_managers import switch_language

from .conf import settings as email_settings


class Email:
    """ A simple wrapper around the post_office.mail.send function.

    This allow to perform additional operations such as generating the text content
    of an email using its HTML content.
    """
    def __init__(
            self, recipient, html_template, text_template=None, subject='', from_email=None,
            subject_template=None, extra_context={}, language=None, attachments={}, tag=None):
        self.recipient = recipient if not email_settings.USE_DEBUG_EMAIL \
            else email_settings.DEBUG_EMAIL_ADDRESS
        self.language = language if language else translation.get_language()
        self.attachments = attachments
        self.from_email = from_email
        self.tag = tag
        with switch_language(self.language):
            self.context = {
                'site': Site.objects.get_current(),
            }
            self.context.update(extra_context)

            self.subject = self._render_template(subject_template).strip() if subject_template \
                else force_text(subject)
            self.html_message = self._render_template(html_template)
            self.text_message = self._render_template(text_template) if text_template \
                else html2text.html2text(self.html_message)

    def send(self):

        kwargs = {
            'subject': self.subject,
            'html_message': self.html_message,
            'message': self.text_message,
            'language': self.language,
            'attachments': self.attachments,
        }

        if self.tag:
            kwargs["headers"] = {'X-Mailgun-Tag': self.tag}

        if self.from_email:
            mail.send(self.recipient, self.from_email, **kwargs)
        else:
            mail.send(self.recipient, **kwargs)

    def _render_template(self, template_name):
        return render_to_string(template_name, self.context)
