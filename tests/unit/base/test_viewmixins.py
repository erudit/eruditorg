# -*- coding: utf-8 -*-

from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.views.generic import View

from base.viewmixins import FedoraServiceRequiredMixin
from base.viewmixins import SolrServiceRequiredMixin


@override_settings(FEDORA_ROOT='http://localhost:800/fedora/')
class TestFedoraServiceRequiredMixin(TestCase):
    def setUp(self):
        super(TestFedoraServiceRequiredMixin, self).setUp()
        self.factory = RequestFactory()

    def test_can_determine_if_the_fedora_service_is_unavailable(self):
        # Setup
        class MyView(FedoraServiceRequiredMixin, View):
            def dispatch(self, request, *args, **kwargs):
                super(MyView, self).dispatch(request, *args, **kwargs)
                return 'ok'

        request = self.factory.get('/')
        view = MyView()

        # Run
        view.dispatch(request)

        # Check
        self.assertFalse(view.fedora_service_available)


@override_settings(SOLR_ADMIN='http://localhost:800/solr/admin/cores/')
class TestSolrServiceRequiredMixin(TestCase):
    def setUp(self):
        super(TestSolrServiceRequiredMixin, self).setUp()
        self.factory = RequestFactory()

    def test_can_determine_if_the_fsolr_service_is_unavailable(self):
        # Setup
        class MyView(SolrServiceRequiredMixin, View):
            def dispatch(self, request, *args, **kwargs):
                super(MyView, self).dispatch(request, *args, **kwargs)
                return 'ok'

        request = self.factory.get('/')
        view = MyView()

        # Run
        view.dispatch(request)

        # Check
        self.assertFalse(view.solr_service_available)
