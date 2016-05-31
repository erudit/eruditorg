# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


section_apps_urlpatterns = [
    url(r'^$', views.HomeView.as_view(), name='home'),
    url(_(r'^autorisations/'),
        include('apps.userspace.library.authorization.urls', namespace='authorization')),
    url(_(r'^membres/'), include('apps.userspace.library.members.urls', namespace='members')),
    url(_(r'^plages-ip/'),
        include('apps.userspace.library.subscription_ips.urls', namespace='subscription_ips')),
    url(_(r'^statistiques/'), include('apps.userspace.library.stats.urls', namespace='stats')),
]

urlpatterns = [
    url(r'^$', views.LibrarySectionEntryPointView.as_view(), name='entrypoint'),
    url(r'^(?:(?P<organisation_pk>\d+)/)?', include(section_apps_urlpatterns)),
]
