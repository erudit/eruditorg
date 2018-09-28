# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = "citations"

urlpatterns = [
    url(r'^$', views.SavedCitationListView.as_view(), name='list'),
    url(_(r'^ajout/$'),
        views.SavedCitationAddView.as_view(), name='add_citation'),
    url(_(r'^suppression/$'),
        views.SavedCitationRemoveView.as_view(), name='remove_citation'),
    url(_(r'^suppression/batch/$'),
        views.SavedCitationBatchRemoveView.as_view(), name='remove_citation_batch'),
    url(_(r'^export\.enw$'), views.EruditDocumentsEnwCitationView.as_view(), name='citation_enw'),
    url(_(r'^export\.ris$'), views.EruditDocumentsRisCitationView.as_view(), name='citation_ris'),
    url(_(r'^export\.bib$'), views.EruditDocumentsBibCitationView.as_view(), name='citation_bib'),
]
