import pytest
from django.contrib.contenttypes.models import ContentType

from erudit.test.factories import JournalFactory

from base.test.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization

from apps.userspace.journal.editor.forms import IssueSubmissionForm

pytestmark = pytest.mark.django_db


def authorize_user_on_journal(user, journal):
    ct = ContentType.objects.get(app_label="erudit", model="journal")
    Authorization.objects.create(
        content_type=ct,
        user=user,
        object_id=journal.id,
        authorization_codename=AC.can_manage_issuesubmission.codename,
    )


def test_contact_filter():
    user = UserFactory()
    user2 = UserFactory()

    journal_in = JournalFactory()
    journal_in.members.add(user)
    journal_in.save()

    journal_not_in = JournalFactory()
    journal_not_in.members.add(user2)
    journal_not_in.save()

    data = {"user": user, "journal": journal_in}

    form = IssueSubmissionForm(**data)
    choices = [c[0] for c in form.fields["contact"].choices]
    assert user.id in choices
    assert user2.id not in choices
