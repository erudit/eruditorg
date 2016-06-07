# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.test import RequestFactory

from erudit.test import BaseEruditTestCase
from erudit.test.factories import OrganisationFactory
from ..templatetags.userspace_library_tags import library_url


class TestLibraryUrlSimpleTag(BaseEruditTestCase):
    def test_can_resolve_the_current_url_for_another_organisation(self):
        # Setup
        org_1 = OrganisationFactory.create()
        org_2 = OrganisationFactory.create()
        factory = RequestFactory()
        base_url = reverse(
            'userspace:library:home', kwargs={'organisation_pk': org_1.pk})
        request = factory.get(base_url)
        request.resolver_match = resolve(base_url)
        # Run
        url = library_url({'request': request}, org_2)
        # Check
        self.assertEqual(
            url,
            reverse('userspace:library:home', kwargs={'organisation_pk': org_2.pk}))
