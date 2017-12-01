# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

import waffle

from . import views


def get_stats_url():
    if waffle.switch_is_active("new_stats"):
        return url(_(r'^statistiques/'), include('apps.userspace.library.stats.new.urls', namespace='stats'))  # noqa
    return url(_(r'^statistiques/'), include('apps.userspace.library.stats.legacy.urls', namespace='stats'))  # noqa


section_apps_urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(_(r'^autorisations/'),
        include('apps.userspace.library.authorization.urls', namespace='authorization')),
    url(_(r'^membres/'), include('apps.userspace.library.members.urls', namespace='members')),
    url(_(r'^informations/'),
        include('apps.userspace.library.subscription_information.urls',
                namespace='subscription_information')),
    url(_(r'^plages-ip/'),
        include('apps.userspace.library.subscription_ips.urls', namespace='subscription_ips')),
    get_stats_url(),
    url(
        _(r'^connexion/'), include(
            'apps.userspace.library.connection.urls', namespace='connection')
    ),
    url(
        _(r'^diagnosis/'), include(
            'apps.userspace.library.diagnosis.urls', namespace='diagnosis')
    ),
    url(
        _(r'^collection/'), include(
            'apps.userspace.library.collection.urls', namespace='collection')
    ),

]

urlpatterns = [
    url(r'^$', views.LibrarySectionEntryPointView.as_view(), name='entrypoint'),
    url(r'^(?:(?P<organisation_pk>\d+)/)?', include(section_apps_urlpatterns)),
]
