# -*- coding: utf-8 -*-

import logging
from urllib.parse import urljoin

from django.conf import settings
from pysolr import SolrCoreAdmin
import requests
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)


class FedoraServiceRequiredMixin(object):
    def check_fedora_status(self, request):
        """ Returns a boolean indicating if the Fedora service is available. """
        status = True
        fedora_url = urljoin(settings.FEDORA_ROOT, 'describe')
        try:
            requests.get(fedora_url, timeout=1)
        except ConnectionError:
            # The Fedora repository is not accessible!
            logger.error('Fedora repository unavailable', exc_info=True, extra={
                'request': request, })
            status = False
        return status

    def get_context_data(self, **kwargs):
        context = super(FedoraServiceRequiredMixin, self).get_context_data(**kwargs)
        context['fedora_service_available'] = self.fedora_service_available
        return context

    def dispatch(self, request, *args, **kwargs):
        self.fedora_service_available = self.check_fedora_status(request)
        return super(FedoraServiceRequiredMixin, self).dispatch(request, *args, **kwargs)


class SolrServiceRequiredMixin(object):
    def check_solr_status(self, request):
        """ Returns a boolean indicating if the Solr service is available. """
        status = True
        solr_admin = SolrCoreAdmin(settings.SOLR_ADMIN)
        try:
            solr_admin.status()
        except ConnectionError:
            # The Solr index is not accessible!
            logger.error('Solr index unavailable', exc_info=True, extra={
                'request': request, })
            status = False
        return status

    def get_context_data(self, **kwargs):
        context = super(SolrServiceRequiredMixin, self).get_context_data(**kwargs)
        context['solr_service_available'] = self.solr_service_available
        return context

    def dispatch(self, request, *args, **kwargs):
        self.solr_service_available = self.check_solr_status(request)
        return super(SolrServiceRequiredMixin, self).dispatch(request, *args, **kwargs)
