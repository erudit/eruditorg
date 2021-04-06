# -*- coding: utf-8 -*-

from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "members"

urlpatterns = [
    re_path(r"^$", views.OrganisationMemberListView.as_view(), name="list"),
    re_path(_(r"^ajout/$"), views.OrganisationMemberCreateView.as_view(), name="create"),
    re_path(
        _(r"^supprimer/(?P<pk>[0-9]+)/$"),
        views.OrganisationMemberDeleteView.as_view(),
        name="delete",
    ),
    re_path(
        _(r"^annuler/(?P<pk>[0-9]+)/$"), views.OrganisationMemberCancelView.as_view(), name="cancel"
    ),
]
