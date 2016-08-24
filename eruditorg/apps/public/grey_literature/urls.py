# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.SearchUnitListView.as_view(), name='search_unit_list'),
    url(_(r'^(?P<code>[\w-]+)/$'), views.SearchUnitDetailView.as_view(),
        name='search_unit_detail'),
    url(_(r'^(?P<code>[\w-]+)/(?P<localid>[\w-]+)/$'),
        views.SearchUnitCollectionDetailView.as_view(), name='collection_detail'),

    url(_(r'^(?P<code>[\w-]+)/(?P<collection_localid>[\w-]+)/(?P<localid>[\w-]+)/'), include([
        url(r'^$', views.SearchUnitDocumentDetailView.as_view(), name='document_detail'),
        url(_(r'^citation\.enw$'), views.SearchUnitDocumentEnwCitationView.as_view(), name='document_citation_enw'),  # noqa
        url(_(r'^citation\.ris$'), views.SearchUnitDocumentRisCitationView.as_view(), name='document_citation_ris'),  # noqa
        url(_(r'^citation\.bib$'), views.SearchUnitDocumentBibCitationView.as_view(), name='document_citation_bib'),  # noqa
    ])),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
