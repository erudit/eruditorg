# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType

from base.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization
from erudit.test import BaseEruditTestCase
from erudit.test.factories import JournalFactory

from ..forms import IssueSubmissionForm


class IssueSubmissionTestCase(BaseEruditTestCase):

    def authorize_user_on_journal(self, user, journal):
        ct = ContentType.objects.get(
            app_label="erudit", model="journal")
        Authorization.objects.create(
            content_type=ct,
            user=user,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename)

    def test_contact_filter(self):
        user = UserFactory()
        user2 = UserFactory()

        journal_in = JournalFactory(collection=self.collection)
        journal_in.members.add(user)
        journal_in.save()

        journal_not_in = JournalFactory(collection=self.collection)
        journal_not_in.members.add(user2)
        journal_not_in.save()

        data = {'user': user, 'journal': journal_in}

        form = IssueSubmissionForm(**data)
        choices = [c[0] for c in form.fields['contact'].choices]
        self.assertTrue(user.id in choices)
        self.assertFalse(user2.id in choices)
