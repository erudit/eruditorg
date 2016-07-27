# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from base.test.testcases import EruditClientTestCase
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory


class TestJournalRoyaltyListView(EruditClientTestCase):
    def test_cannot_be_accessed_by_a_user_who_cannot_consult_royalty_reports(self):
        # Setup
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('userspace:journal:royalty_reports:list', args=(self.journal.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 403

    def test_can_be_accessed_by_a_user_who_can_consult_royalty_reports(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.journal), object_id=self.journal.id,
            user=self.user, authorization_codename=AC.can_consult_royalty_reports.codename)
        self.client.login(username='foo', password='notreallysecret')
        url = reverse('userspace:journal:royalty_reports:list', args=(self.journal.pk, ))
        # Run
        response = self.client.get(url)
        # Check
        assert response.status_code == 200
