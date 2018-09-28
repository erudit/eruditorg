import pytest

from django.conf import settings
from django.urls import reverse
from django.test.client import Client
from django.test.utils import override_settings

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory, JournalInformationFactory

from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.models import Authorization


pytestmark = pytest.mark.django_db

@override_settings(DEBUG=True)
def test_can_insert_the_journal_information_into_the_context():
    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    Authorization.authorize_user(user, journal, AC.can_edit_journal_information)

    client = Client()
    client.login(username=user.username, password='default')

    jinfo = JournalInformationFactory.create(journal=journal)
    url = reverse('userspace:journal:home', args=(journal.pk, ))
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['journal_info'] == jinfo


def test_report_download_contents(monkeypatch, tmpdir):
    monkeypatch.setattr(settings, 'SUBSCRIPTION_EXPORTS_ROOT', str(tmpdir))

    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])
    Authorization.authorize_user(user, journal, AC.can_consult_royalty_reports)

    tmpdir.join(journal.code, 'Abonnements', 'Rapports', '2017.csv').ensure().write('hello')

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:reports_download') + '?subpath=Abonnements/Rapports/2017.csv'
    response = client.get(url, follow=True)
    assert response.content == b'hello'

    url = reverse('userspace:journal:reports_download') + '?subpath=Abonnements/Rapports/2016.csv'
    response = client.get(url, follow=True)
    assert response.status_code == 404

