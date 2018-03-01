from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


section_apps_urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(_(r'^autorisations/'),
        include('apps.userspace.journal.authorization.urls', namespace='authorization')),
    url(_(r'^editeur/'),
        include('apps.userspace.journal.editor.urls', namespace='editor')),
    url(_(r'^informations/'),
        include('apps.userspace.journal.information.urls', namespace='information')),
    url(_(r'^abonnements/'),
        include('apps.userspace.journal.subscription.urls', namespace='subscription')),
    url(
        _(r'^redevances/$'),
        views.RoyaltiesListView.as_view(),
        name='royalty_reports'
    ),
    url(
        _(r'^redevances/telecharger/$'),
        views.RoyaltyReportsDownload.as_view(),
        name='reports_download'
    ),
]

urlpatterns = [
    url(r'^$', views.JournalSectionEntryPointView.as_view(), name='entrypoint'),
    url(r'^(?:(?P<journal_pk>\d+)/)?', include(section_apps_urlpatterns)),
]
