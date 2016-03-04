import factory

from base.factories import UserFactory
from erudit.factories import JournalFactory


class IssueSubmissionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'editor.IssueSubmission'

    journal = factory.SubFactory(JournalFactory)
    contact = factory.SubFactory(UserFactory)
