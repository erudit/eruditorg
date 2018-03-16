from django.test import RequestFactory
from django.views.generic import View

from base.viewmixins import FedoraServiceRequiredMixin
from base.viewmixins import SolrServiceRequiredMixin


def test_can_determine_if_the_fedora_service_is_unavailable():
    class MyView(FedoraServiceRequiredMixin, View):
        _pytest_check_fedora_status_result = False

        def dispatch(self, request, *args, **kwargs):
            super(MyView, self).dispatch(request, *args, **kwargs)
            return 'ok'

    request = RequestFactory().get('/')
    view = MyView()
    view.dispatch(request)
    assert not view.fedora_service_available


def test_can_determine_if_the_fsolr_service_is_unavailable():
    class MyView(SolrServiceRequiredMixin, View):
        _pytest_check_solr_status_result = False

        def dispatch(self, request, *args, **kwargs):
            super(MyView, self).dispatch(request, *args, **kwargs)
            return 'ok'

    request = RequestFactory().get('/')
    view = MyView()
    view.dispatch(request)
    assert not view.solr_service_available
