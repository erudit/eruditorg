from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "journal"

section_apps_urlpatterns = [
    re_path(r"^$", views.HomeView.as_view(), name="home"),
    re_path(_(r"^autorisations/"), include("apps.userspace.journal.authorization.urls")),
    re_path(_(r"^editeur/"), include("apps.userspace.journal.editor.urls")),
    re_path(_(r"^informations/"), include("apps.userspace.journal.information.urls")),
    re_path(_(r"^abonnements/"), include("apps.userspace.journal.subscription.urls")),
    re_path(_(r"^redevances/$"), views.RoyaltiesListView.as_view(), name="royalty_reports"),
    re_path(
        _(r"^redevances/telecharger/$"),
        views.RoyaltyReportsDownload.as_view(),
        name="reports_download",
    ),
]

urlpatterns = [
    re_path(r"^$", views.JournalSectionEntryPointView.as_view(), name="entrypoint"),
    re_path(r"^(?:(?P<journal_pk>\d+)/)?", include(section_apps_urlpatterns)),
]
