import pytest
from django.urls import resolve
from django.urls import reverse
from django.test import RequestFactory

from erudit.test.factories import OrganisationFactory

from apps.userspace.library.templatetags.userspace_library_tags import library_url

pytestmark = pytest.mark.django_db


def test_can_resolve_the_current_url_for_another_organisation():
    org_1 = OrganisationFactory.create()
    org_2 = OrganisationFactory.create()
    factory = RequestFactory()
    base_url = reverse("userspace:library:home", kwargs={"organisation_pk": org_1.pk})
    request = factory.get(base_url)
    request.resolver_match = resolve(base_url)
    url = library_url({"request": request}, org_2)
    EXPECTED = reverse("userspace:library:home", kwargs={"organisation_pk": org_2.pk})
    assert url == EXPECTED
