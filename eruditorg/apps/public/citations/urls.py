# -*- coding: utf-8 -*-

from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "citations"

urlpatterns = [
    re_path(r"^$", views.SavedCitationListView.as_view(), name="list"),
    re_path(_(r"^ajout/$"), views.SavedCitationAddView.as_view(), name="add_citation"),
    re_path(_(r"^suppression/$"), views.SavedCitationRemoveView.as_view(), name="remove_citation"),
    re_path(
        _(r"^suppression/batch/$"),
        views.SavedCitationBatchRemoveView.as_view(),
        name="remove_citation_batch",
    ),
    re_path(
        _(r"^export\.enw$"), views.EruditDocumentsEnwCitationView.as_view(), name="citation_enw"
    ),
    re_path(
        _(r"^export\.ris$"), views.EruditDocumentsRisCitationView.as_view(), name="citation_ris"
    ),
    re_path(
        _(r"^export\.bib$"), views.EruditDocumentsBibCitationView.as_view(), name="citation_bib"
    ),
]
