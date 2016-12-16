# -*- coding: utf-8 -*-

from django.conf.urls import include
from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page

from . import urls_compat
from . import views


urlpatterns = [
    url(
        r'^$',
        cache_page(60 * 15)(views.ThesisHomeView.as_view()),
        name='home'
    ),
    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/$'),
        cache_page(60 * 15)(views.ThesisCollectionHomeView.as_view()),
        name='collection_home'
    ),

    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/(?P<publication_year>[\d-]+)/$'),
        cache_page(60 * 15)(views.ThesisPublicationYearListView.as_view()),
        name='collection_list_per_year'
    ),
    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/(?P<author_letter>[\w\'-])/$'),
        cache_page(60 * 15)(views.ThesisPublicationAuthorNameListView.as_view()),
        name='collection_list_per_author_name'
    ),

    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.enw$'),
        cache_page(60 * 15)(views.ThesisEnwCitationView.as_view()),
        name='thesis_citation_enw'
    ),
    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.ris$'),
        cache_page(60 * 15)(views.ThesisRisCitationView.as_view()),
        name='thesis_citation_ris'
    ),
    url(
        _(r'^fonds/(?P<collection_pk>[\d-]+)/t/(?P<pk>\d+)\.bib$'),
        cache_page(60 * 15)(views.ThesisBibCitationView.as_view()),
        name='thesis_citation_bib'
    ),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]
