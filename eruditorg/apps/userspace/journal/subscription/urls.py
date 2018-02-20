from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^individuel/$'),
        views.IndividualJournalAccessSubscriptionListView.as_view(), name='list'),
    url(_(r'^individuel/ajout/'),
        views.IndividualJournalAccessSubscriptionCreateView.as_view(), name='create'),
    url(_(r'^individuel/supprimer/(?P<pk>[0-9]+)/$'),
        views.IndividualJournalAccessSubscriptionDeleteView.as_view(), name='delete'),
    url(_(r'^individuel/annuler/(?P<pk>[0-9]+)/$'),
        views.IndividualJournalAccessSubscriptionCancelView.as_view(), name='cancel'),
    url(_(r'^institutionnel/$'),
        views.JournalOrganisationSubscriptionList.as_view(), name='org_list'),
    url(_(r'^institutionnel/exports/$'),
        views.JournalOrganisationSubscriptionExport.as_view(), name='org_export'),
    url(
        _(r'^institutionnel/exports/telecharger/$'),
        views.JournalOrganisationSubscriptionExportDownload.as_view(),
        name='org_export_download'
    ),
]
