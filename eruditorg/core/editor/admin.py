# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import IssueSubmission
from .models import IssueSubmissionFilesVersion
from .models import ProductionTeam


class IssueSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "journal", "contact", "status", "date_created", "date_modified", "url")
    list_filter = ("status", "journal")

    def url(self, obj):
        return format_html("<a href={}>{}</a>", obj.get_absolute_url(), _("Voir sur le site"))


class IssueSubmissionFilesVersionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "issue_submission",
        "files_count",
    )

    def files_count(self, obj):
        return obj.submissions.count()

    files_count.short_description = _("Nombre de fichiers")


class ProductionTeamAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "group",
    )
    filter_horizontal = ("journals",)


admin.site.register(IssueSubmission, IssueSubmissionAdmin)
admin.site.register(IssueSubmissionFilesVersion, IssueSubmissionFilesVersionAdmin)
admin.site.register(ProductionTeam, ProductionTeamAdmin)
