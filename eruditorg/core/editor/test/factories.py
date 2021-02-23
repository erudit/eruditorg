# -*- coding: utf-8 -*-

import factory

from erudit.test.factories import JournalFactory

from base.test.factories import GroupFactory
from base.test.factories import UserFactory


class IssueSubmissionFactory(factory.django.DjangoModelFactory):
    journal = factory.SubFactory(JournalFactory)
    contact = factory.SubFactory(UserFactory)

    class Meta:
        model = "editor.IssueSubmission"


class ProductionTeamFactory(factory.django.DjangoModelFactory):
    group = factory.SubFactory(GroupFactory)

    class Meta:
        model = "editor.ProductionTeam"
