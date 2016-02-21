# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _

from navutils import BreadcrumbsMixin, Breadcrumb


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return login_required(view)


class UserspaceBreadcrumbsMixin(BreadcrumbsMixin):
    def get_breadcrumbs(self):
        breadcrumbs = super(UserspaceBreadcrumbsMixin, self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(_("Mon espace"),
                                      pattern_name='userspace:dashboard'))
        return breadcrumbs
