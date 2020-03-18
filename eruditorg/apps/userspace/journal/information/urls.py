# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "information"

urlpatterns = [
    url(_(r'^$'),
        views.JournalInformationUpdateView.as_view(), name='update'),
    url(_(r'^supprimer_collaborateur$'),
        views.JournalInformationCollaboratorDeleteView.as_view(), name='delete_contributor'),
]
