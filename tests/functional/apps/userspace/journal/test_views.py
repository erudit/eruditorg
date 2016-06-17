# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from erudit.test.factories import JournalInformationFactory

from base.test.testcases import EruditClientTestCase
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


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
