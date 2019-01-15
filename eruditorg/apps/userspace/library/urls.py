# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.db.utils import ProgrammingError
from django.utils.translation import ugettext_lazy as _

import waffle

from . import views

app_name = "library"


def get_stats_url():
    try:
        new_stats_active = waffle.switch_is_active("new_stats")
    except ProgrammingError:
        # we're performing an initial migration
        new_stats_active = False
    if new_stats_active:
        return url(_(r'^statistiques/'), include('apps.userspace.library.stats.new.urls'))  # noqa
    return url(_(r'^statistiques/'), include('apps.userspace.library.stats.legacy.urls'))  # noqa


section_apps_urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(_(r'^autorisations/'),
        include('apps.userspace.library.authorization.urls')),
    url(_(r'^membres/'), include('apps.userspace.library.members.urls')),
    url(_(r'^informations/'),
        include('apps.userspace.library.subscription_information.urls',)),
    url(_(r'^plages-ip/'),
        include('apps.userspace.library.subscription_ips.urls')),
    get_stats_url(),
    url(
        _(r'^connexion/'), include(
            'apps.userspace.library.connection.urls')
    ),
    url(
        _(r'^diagnosis/'), include(
            'apps.userspace.library.diagnosis.urls')
    ),
    url(
        _(r'^collection/'), include(
            'apps.userspace.library.collection.urls')
    ),

]

urlpatterns = [
    url(r'^$', views.LibrarySectionEntryPointView.as_view(), name='entrypoint'),
    url(r'^(?:(?P<organisation_pk>\d+)/)?', include(section_apps_urlpatterns)),
]
