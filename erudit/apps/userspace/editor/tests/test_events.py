from django.core.urlresolvers import reverse

from erudit.models import Event
from core.editor.models import IssueSubmission
from core.editor.tests.base import BaseEditorTestCase


class TestIssueSubmissionEvents(BaseEditorTestCase):
    def test_issuesubmission_creation_triggers_event(self):
        """ Creating a new issue submission creates an Event
        """
        event_count = Event.objects.count()

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

        self.assertEquals(
            Event.objects.count(),
            event_count + 1,
            "An event should have been added"
        )

        event = Event.objects.last()
        submission = IssueSubmission.objects.last()

        self.assertEquals(event.type, Event.TYPE_SUBMISSION_CREATED)
        self.assertEquals(event.author, self.user)
        self.assertEquals(event.target_object, submission)
