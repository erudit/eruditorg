# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import urls_compat
from . import views


urlpatterns = [
    url(r'^$', views.ThesisHomeView.as_view(), name='home'),
    url(_(r'^fond/(?P<collection_pk>[\d-]+)/$'),
        views.ThesisCollectionHomeView.as_view(), name='collection_home'),

    url(_(r'^fond/(?P<collection_pk>[\d-]+)/liste/annee/(?P<publication_year>[\d-]+)/$'),
        views.ThesisPublicationYearListView.as_view(), name='collection_list_per_year'),
    url(_(r'^fond/(?P<collection_pk>[\d-]+)/liste/auteur/(?P<author_letter>[\w-])/$'),
        views.ThesisPublicationAuthorNameListView.as_view(),
        name='collection_list_per_author_name'),

    url(_(r'^fond/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.enw$'),
        views.ThesisEnwCitationView.as_view(), name='thesis_citation_enw'),
    url(_(r'^fond/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.ris$'),
        views.ThesisRisCitationView.as_view(), name='thesis_citation_ris'),
    url(_(r'^fond/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.bib$'),
        views.ThesisBibCitationView.as_view(), name='thesis_citation_bib'),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
