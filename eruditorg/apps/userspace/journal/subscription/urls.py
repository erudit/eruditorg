from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "subscription"

urlpatterns = [
    re_path(
        _(r"^individuel/$"),
        views.IndividualJournalAccessSubscriptionListView.as_view(),
        name="list",
    ),
    re_path(
        _(r"^individuel/abonner/"),
        views.IndividualJournalAccessSubscriptionCreateView.as_view(),
        name="create",
    ),
    re_path(
        _(r"^individuel/supprimer-par-courriel/"),
        views.IndividualJournalAccessSubscriptionDeleteByEmailView.as_view(),
        name="delete_by_email",
    ),
    re_path(
        _(r"^individuel/supprimer/(?P<pk>[0-9]+)/$"),
        views.IndividualJournalAccessSubscriptionDeleteView.as_view(),
        name="delete",
    ),
    re_path(
        _(r"^individuel/annuler/(?P<pk>[0-9]+)/$"),
        views.IndividualJournalAccessSubscriptionCancelView.as_view(),
        name="cancel",
    ),
    re_path(
        _(r"^individuel/abonner-en-lot/"),
        views.JournalIndividualSubscriptionBatchSubscribe.as_view(),
        name="batch_subscribe",
    ),
    re_path(
        _(r"^individuel/supprimer-en-lot/"),
        views.JournalIndividualSubscriptionBatchDelete.as_view(),
        name="batch_delete",
    ),
    re_path(
        _(r"^institutionnel/$"),
        views.JournalOrganisationSubscriptionList.as_view(),
        name="org_list",
    ),
    re_path(
        _(r"^institutionnel/exports/$"),
        views.JournalOrganisationSubscriptionExport.as_view(),
        name="org_export",
    ),
    re_path(
        _(r"^institutionnel/exports/telecharger/$"),
        views.JournalOrganisationSubscriptionExportDownload.as_view(),
        name="org_export_download",
    ),
]
