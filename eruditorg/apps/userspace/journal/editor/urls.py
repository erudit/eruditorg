from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "editor"

urlpatterns = [
    re_path(_(r"^numero/$"), views.IssueSubmissionListView.as_view(), name="issues"),
    re_path(_(r"^numero/ajout/$"), views.IssueSubmissionCreate.as_view(), name="add"),
    re_path(
        _(r"^numero/(?P<pk>[0-9]+)/$"),
        views.IssueSubmissionDetailView.as_view(),
        name="detail",
    ),
    re_path(
        _(r"^numero/(?P<pk>[0-9]+)/edition/$"),
        views.IssueSubmissionUpdate.as_view(),
        name="update",
    ),
    re_path(
        _(r"^numero/(?P<pk>[0-9]+)/approuver/$"),
        views.IssueSubmissionApproveView.as_view(),
        name="transition_approve",
    ),
    re_path(
        _(r"^numero/(?P<pk>[0-9]+)/refuser/$"),
        views.IssueSubmissionRefuseView.as_view(),
        name="transition_refuse",
    ),
    re_path(
        _(r"^numero/(?P<pk>[0-9]+)/supprimer/$"),
        views.IssueSubmissionDeleteView.as_view(),
        name="delete",
    ),
    re_path(
        _(r"^numero/fichier/(?P<pk>[0-9]+)/$"),
        views.IssueSubmissionAttachmentView.as_view(),
        name="attachment_detail",
    ),
]
