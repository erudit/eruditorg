import pytest
from django.urls import reverse
from base.test.factories import logged_client, UserFactory
from erudit.test.factories import JournalFactory, OrganisationFactory

pytestmark = pytest.mark.django_db


def test_userspacehome_unprivileged():
    # An unprivileged user is redirected to her settings view
    client = logged_client()
    url = reverse("userspace:dashboard")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("public:auth:personal_data")


def test_userspacehome_editor():
    # An editor is redirected properly
    user = UserFactory.create()
    journal = JournalFactory.create()
    journal.members.add(user)
    client = logged_client(user)
    url = reverse("userspace:dashboard")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("userspace:journal:home")


def test_userspacehome_library():
    # An library is redirected properly
    user = UserFactory.create()
    org = OrganisationFactory.create()
    org.members.add(user)
    client = logged_client(user)
    url = reverse("userspace:dashboard")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == reverse("userspace:library:home")


def test_userspacehome_superuser():
    # A superuser is presented with a choice directly rendered (without redirect)
    user = UserFactory.create()
    journal = JournalFactory.create()
    journal.members.add(user)
    org = OrganisationFactory.create()
    org.members.add(user)
    client = logged_client(user)
    url = reverse("userspace:dashboard")
    response = client.get(url)
    assert response.status_code == 200
