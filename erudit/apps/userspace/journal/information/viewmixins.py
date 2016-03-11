# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

from navutils import Breadcrumb

from apps.userspace.viewmixins import UserspaceBreadcrumbsMixin


class JournalBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(JournalBreadcrumbsMixin,
                            self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Revues"),
            pattern_name='userspace:journal:information:update'))
        return breadcrumbs
