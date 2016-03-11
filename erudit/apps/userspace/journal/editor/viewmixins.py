from django.utils.translation import ugettext_lazy as _

from navutils import Breadcrumb
from rules.contrib.views import PermissionRequiredMixin

from apps.userspace.viewmixins import LoginRequiredMixin
from apps.userspace.viewmixins import UserspaceBreadcrumbsMixin


class IssueSubmissionBreadcrumbsMixin(UserspaceBreadcrumbsMixin):

    def get_breadcrumbs(self):
        breadcrumbs = super(IssueSubmissionBreadcrumbsMixin,
                            self).get_breadcrumbs()
        breadcrumbs.append(Breadcrumb(
            _("Dépôts de numéros"),
            pattern_name='userspace:journal:editor:issues'))
        return breadcrumbs


class IssueSubmissionCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'editor.manage_issuesubmission'

    def get_queryset(self):
        qs = super(IssueSubmissionCheckMixin, self).get_queryset()
        ids = [issue.id for issue in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', issue.journal)]
        return qs.filter(id__in=ids)
