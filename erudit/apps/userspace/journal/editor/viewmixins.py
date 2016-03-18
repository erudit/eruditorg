# -*- coding: utf-8 -*-

from rules.contrib.views import PermissionRequiredMixin


class IssueSubmissionCheckMixin(PermissionRequiredMixin):
    permission_required = 'editor.manage_issuesubmission'

    def get_queryset(self):
        qs = super(IssueSubmissionCheckMixin, self).get_queryset()
        ids = [issue.id for issue in qs if self.request.user.has_perm(
               'editor.manage_issuesubmission', issue.journal)]
        return qs.filter(id__in=ids)
