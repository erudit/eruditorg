# -*- coding: utf-8 -*-

from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "information"

urlpatterns = [
    re_path(_(r"^$"), views.JournalInformationUpdateView.as_view(), name="update"),
    re_path(
        _(r"^supprimer_collaborateur$"),
        views.JournalInformationCollaboratorDeleteView.as_view(),
        name="delete_contributor",
    ),
]
