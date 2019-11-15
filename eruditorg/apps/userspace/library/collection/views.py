# -*- coding: utf-8 -*-
import requests
from datetime import datetime

from django.views.generic import FormView
from django.http.response import HttpResponse

from django.conf import settings

from base.viewmixins import MenuItemMixin

from ...generic_apps.authorization.views import AuthorizationUserView as BaseAuthorizationUserView

from ..viewmixins import OrganisationScopePermissionRequiredMixin
from .forms import KBARTForm


ERUDIT_KBART_BACKEND_URL = getattr(
    settings,
    "ERUDIT_KBART_BACKEND_URL",
    "http://kbart-backend.local"
)


ERUDIT_KBART_2014_BACKEND_URL = getattr(
    settings,
    "ERUDIT_KBART_2014_BACKEND_URL",
    "http://kbart-backend.local"
)


class CollectionView(
        OrganisationScopePermissionRequiredMixin,
        MenuItemMixin, BaseAuthorizationUserView, FormView):
    menu_library = 'collection'
    permission_required = 'library.has_access_to_dashboard'
    template_name = 'userspace/library/collection/landing.html'
    form_class = KBARTForm

    def get_target_instance(self):
        return self.current_organisation

    def form_valid(self, form):

        if form.cleaned_data['version'] == '2009':
            report_url = ERUDIT_KBART_BACKEND_URL
        else:
            report_url = ERUDIT_KBART_2014_BACKEND_URL

        report = requests.get(report_url, params=form.cleaned_data)
        filename = "Erudit_Global_{type}_{date}_{collection}_{access}".format(
            type=form.cleaned_data['typeRevue']
            if form.cleaned_data['typeRevue'] != 'all' else 'AllTitles',
            date=datetime.now().strftime("%Y-%m-%d"),
            collection=form.cleaned_data['collection']
            if form.cleaned_data['collection'] != 'all' else 'Global',
            access=form.cleaned_data['access']
            if form.cleaned_data['access'] != 'all' else 'Global',
        )

        response = HttpResponse(
            report, content_type="application/txt"
        )

        response['Content-Disposition'] = 'attachment; filename="{filename}.txt"'.format(
            filename=filename,
        )

        return response
