# -*- coding: utf-8 -*-

from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "authorization"

urlpatterns = [
    re_path(r"^$", views.AuthorizationUserView.as_view(), name="list"),
    re_path(_(r"^ajout/$"), views.AuthorizationCreateView.as_view(), name="create"),
    re_path(
        _(r"^(?P<pk>[0-9]+)/supprimer/$"),
        views.AuthorizationDeleteView.as_view(),
        name="delete",
    ),
]
