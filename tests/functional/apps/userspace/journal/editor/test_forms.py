import pytest
from django.contrib.contenttypes.models import ContentType

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization

pytestmark = pytest.mark.django_db


def authorize_user_on_journal(user, journal):
    ct = ContentType.objects.get(app_label="erudit", model="journal")
    Authorization.objects.create(
        content_type=ct,
        user=user,
        object_id=journal.id,
        authorization_codename=AC.can_manage_issuesubmission.codename,
    )
