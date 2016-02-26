from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import IssueSubmission


class IssueSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'journal',
        'contact',
        '_parent',
        'date_created',
        'date_modified',
    )
    list_filter = ('journal', 'status', )

    def _parent(self, obj):
        if obj.parent:
            return obj.parent.id
        else:
            return dict(IssueSubmission.STATUS_CHOICES)[obj.status]
    _parent.short_description = _("Statut")

admin.site.register(IssueSubmission, IssueSubmissionAdmin)
