from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page

from . import views


urlpatterns = [
    url(
        r'^$',
        cache_page(60 * 15)(views.ThesisHomeView.as_view()),
        name='home'
    ),
    url(
        _(r'^(?P<collection_code>[\w-]+)/$'),
        cache_page(60 * 15)(views.ThesisCollectionHomeView.as_view()),
        name='collection_home'
    ),

    url(
        _(r'^(?P<collection_code>[\w-]+)/(?P<publication_year>[\d-]+)/$'),
        cache_page(60 * 15)(views.ThesisPublicationYearListView.as_view()),
        name='collection_list_per_year'
    ),
    url(
        _(r'^(?P<collection_code>[\w-]+)/(?P<author_letter>[\w\'-])/$'),
        cache_page(60 * 15)(views.ThesisPublicationAuthorNameListView.as_view()),
        name='collection_list_per_author_name'
    ),

    url(
        _(r'^(?P<collection_code>[\w-]+)/t/(?P<solr_id>.+)\.enw$'),
        cache_page(60 * 15)(views.ThesisEnwCitationView.as_view()),
        name='thesis_citation_enw'
    ),
    url(
        _(r'^(?P<collection_code>[\w-]+)/t/(?P<solr_id>.+)\.ris$'),
        cache_page(60 * 15)(views.ThesisRisCitationView.as_view()),
        name='thesis_citation_ris'
    ),
    url(
        _(r'^(?P<collection_code>[\w-]+)/t/(?P<solr_id>.+)\.bib$'),
        cache_page(60 * 15)(views.ThesisBibCitationView.as_view()),
        name='thesis_citation_bib'
    ),

]
