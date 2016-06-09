# -*- coding: utf-8 -*-

import factory

from erudit.test.factories import JournalFactory

from base.test.factories import UserFactory


class IssueSubmissionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'editor.IssueSubmission'

    journal = factory.SubFactory(JournalFactory)
    contact = factory.SubFactory(UserFactory)
