import datetime
import json
import requests
import urllib

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import TemplateView, View
from django.urls import reverse

from django.conf import settings

from base.viewmixins import MenuItemMixin

from ..viewmixins import OrganisationScopePermissionRequiredMixin


class CollectionView(
        LoginRequiredMixin, MenuItemMixin, OrganisationScopePermissionRequiredMixin, TemplateView):
    menu_library = 'collection'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/collection/landing.html'

    def get_target_instance(self):
        return self.current_organisation

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if settings.ABONNEMENTS_BASKETS_BACKEND_URL is None:
            return context
        response = requests.get(
            settings.ABONNEMENTS_BASKETS_BACKEND_URL + str(datetime.datetime.now().year),
            timeout=5,
        )
        if response.status_code == 200:
            context['baskets'] = json.loads(response.content.decode())
            context['kbart2014_download_url'] = reverse(
                'userspace:library:collection:kbart2014_download',
                kwargs={'organisation_pk': kwargs.get('organisation_pk')},
            )
        return context


class Kbart2014FileDownloadView(LoginRequiredMixin, OrganisationScopePermissionRequiredMixin, View):
    """ Proxy view to download files from the KBART 2014 backend. """
    permission_required = 'library.has_access_to_dashboard'

    def get(self, request, *args, **kwargs):
        if settings.KBART_2014_BACKEND_URL is None:
            return HttpResponseNotFound
        response = requests.get(
            settings.KBART_2014_BACKEND_URL + '?{}'.format(urllib.parse.urlencode(request.GET)),
            timeout=120,
        )
        if response.status_code == 200:
            new_response = HttpResponse(response.content)
            new_response['Content-Type'] = response.headers.get('content-type')
            new_response['Content-Disposition'] = response.headers.get('content-disposition')
            return new_response
        else:
            return HttpResponseNotFound
