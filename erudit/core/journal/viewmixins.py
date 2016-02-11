# -*- coding: utf-8 -*-

from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from navutils import Breadcrumb

from erudit.models import Journal
from userspace.views import UserspaceBreadcrumbsMixin


class JournalBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(JournalBreadcrumbsMixin,
                            self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Revues"),
            pattern_name='journal:journal-information'))
        return breadcrumbs


class JournalCodeDetailMixin(object):
    """
    Simply allows retrieving a Journal instance using its code.
    """
    def get_journal(self):
        try:
            return Journal.objects.get(code=self.kwargs['code'])
        except Journal.DoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        return self.get_journal()
