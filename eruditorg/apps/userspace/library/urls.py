# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "library"


section_apps_urlpatterns = [
    re_path(r"^$", views.HomeView.as_view(), name="home"),
    re_path(_(r"^autorisations/"), include("apps.userspace.library.authorization.urls")),
    re_path(_(r"^membres/"), include("apps.userspace.library.members.urls")),
    re_path(
        _(r"^informations/"),
        include(
            "apps.userspace.library.subscription_information.urls",
        ),
    ),
    re_path(_(r"^plages-ip/"), include("apps.userspace.library.subscription_ips.urls")),
    re_path(_(r"^statistiques/"), include("apps.userspace.library.stats.urls")),
    re_path(_(r"^connexion/"), include("apps.userspace.library.connection.urls")),
    re_path(_(r"^diagnosis/"), include("apps.userspace.library.diagnosis.urls")),
    re_path(_(r"^collection/"), include("apps.userspace.library.collection.urls")),
]

urlpatterns = [
    re_path(r"^$", views.LibrarySectionEntryPointView.as_view(), name="entrypoint"),
    re_path(r"^(?:(?P<organisation_pk>\d+)/)?", include(section_apps_urlpatterns)),
]
