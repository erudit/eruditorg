from django.test import TestCase
from django.core.urlresolvers import reverse
from django.http.response import HttpResponseRedirect


# Create your tests here.
class TestJournalSubmissionView(TestCase):

    def test_unlogged_add_journalsubmission(self):
        """ Unlogged users should be redirected to the login page """
        result = self.client.get(reverse('editor:add'))
        self.assertIsInstance(result, HttpResponseRedirect)
        self.assertTrue(
            "?next={}".format(reverse('editor:add')) in result.url
        )
