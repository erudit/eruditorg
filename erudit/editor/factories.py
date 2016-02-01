import factory

from erudit.factories import JournalFactory
from userspace.factories import UserFactory


class IssueSubmissionFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'editor.IssueSubmission'

    journal = factory.SubFactory(JournalFactory)
    contact = factory.SubFactory(UserFactory)
