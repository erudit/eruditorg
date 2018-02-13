import pytest

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.utils import override_settings

from base.test.factories import UserFactory
from erudit.test.factories import JournalFactory, JournalInformationFactory

from base.test.testcases import EruditClientTestCase
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


pytestmark = pytest.mark.django_db

class TestHomeView(EruditClientTestCase):
    @override_settings(DEBUG=True)
    def test_can_insert_the_journal_information_into_the_context(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_edit_journal_information.codename)
        self.client.login(username='foo', password='notreallysecret')
        jinfo = JournalInformationFactory.create(journal=self.journal)
        url = reverse('userspace:journal:home', args=(self.journal.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
        assert response.context['journal_info'] == jinfo


def test_report_download_contents(monkeypatch, tmpdir):
    monkeypatch.setattr(settings, 'SUBSCRIPTION_EXPORTS_ROOT', str(tmpdir))

    user = UserFactory.create()
    journal = JournalFactory.create(members=[user])

    tmpdir.mkdir(journal.code).join('2017.csv').write('hello')

    client = Client()
    client.login(username=user.username, password='default')

    url = reverse('userspace:journal:reports_download') + '?subpath=2017.csv'
    response = client.get(url, follow=True)
    assert response.content == b'hello'

    url = reverse('userspace:journal:reports_download') + '?subpath=2016.csv'
    response = client.get(url, follow=True)
    assert response.status_code == 404

