from django.test import TestCase, RequestFactory
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.contrib.auth.models import User


class TestJournalSubmissionView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='david',
            email='david.cormier@erudit.org',
            password='top_secret'
        )

    def test_unlogged_add_journalsubmission(self):
        """ Unlogged users should be redirected to the login page """
        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertTrue(
            "?next={}".format(reverse('editor:add')) in result.url
        )

    def test_logged_add_journalsubmission(self):
        """ Logged users should be able to see journal submissions """
        self.client.login(username='david', password='top_secret')
        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(result, TemplateResponse)
