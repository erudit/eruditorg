from django.core.urlresolvers import reverse

from erudit.models import Event
from core.editor.models import IssueSubmission
from core.editor.tests.base import BaseEditorTestCase


class TestIssueSubmissionEvents(BaseEditorTestCase):
    def setUp(self):
        super().setUp()
        self.previous_event_count = Event.objects.count()

    def expect_new_event(self):
        self.assertEquals(
            Event.objects.count(),
            self.previous_event_count + 1,
            "An event should have been created"
        )
        result = Event.objects.last()
        self.previous_event_count = Event.objects.count()
        return result

    def test_issuesubmission_creation_triggers_event(self):
        """ Creating a new issue submission creates an Event
        """
        data = {
            'journal': self.journal.pk,
            'year': '2015',
            'volume': '2',
            'number': '2',
            'contact': self.user.pk,
            'comment': 'lorem ipsum dolor sit amet',
        }

        self.client.login(username='david', password='top_secret')

        url = reverse('userspace:editor:add')
        self.client.post(url, data)

        event = self.expect_new_event()
        submission = IssueSubmission.objects.last()

        self.assertEquals(event.type, Event.TYPE_SUBMISSION_CREATED)
        self.assertEquals(event.author, self.user)
        self.assertEquals(event.target_object, submission)

    def test_issuesubmission_status_update_triggers_event(self):
        """ Issue workflow transitions trigger events.

            The comment of that event contains the new and old status.
        """
        self.client.login(username='david', password='top_secret')

        url = reverse('userspace:editor:transition-submit', args=(self.issue_submission.pk, ))
        self.client.post(url)

        event = self.expect_new_event()

        self.assertEquals(event.type, Event.TYPE_SUBMISSION_STATUS_CHANGE)
        self.assertEquals(event.author, self.user)
        self.assertEquals(event.target_object, self.issue_submission)
        self.assertIn(IssueSubmission.DRAFT, event.comment)
        self.assertIn(IssueSubmission.SUBMITTED, event.comment)
