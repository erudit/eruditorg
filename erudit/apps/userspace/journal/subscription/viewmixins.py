from rules.contrib.views import PermissionRequiredMixin

from apps.userspace.viewmixins import LoginRequiredMixin
from core.subscription.models import IndividualAccountProfile


class OrganizationCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'subscription.manage_account'

    def get_queryset(self):
        qs = IndividualAccountProfile.objects.order_by('-id')
        ids = [account.id for account in qs if self.request.user.has_perm(
               'subscription.manage_account', account)]
        return qs.filter(id__in=ids)
