from django.utils.translation import ugettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin
from navutils import Breadcrumb

from core.subscription.models import IndividualAccount
from apps.userspace.viewmixins import (LoginRequiredMixin,
                                       UserspaceBreadcrumbsMixin)


class IndividualAccountBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(IndividualAccountBreadcrumbsMixin,
                            self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Abonnements individuels"),
            pattern_name='userspace:journal:subscription:account_list'))
        return breadcrumbs


class OrganizationCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'subscription.manage_account'

    def get_queryset(self):
        qs = IndividualAccount.objects.order_by('-id')
        ids = [account.id for account in qs if self.request.user.has_perm(
               'subscription.manage_account', account)]
        return qs.filter(id__in=ids)
