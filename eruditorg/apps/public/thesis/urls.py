from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "thesis"

urlpatterns = [
    re_path(r"^$", views.ThesisHomeView.as_view(), name="home"),
    re_path(
        _(r"^(?P<collection_code>[\w-]+)/$"),
        views.ThesisCollectionHomeView.as_view(),
        name="collection_home",
    ),
    re_path(
        _(r"^(?P<collection_code>[\w-]+)/(?P<publication_year>[\d-]+)/$"),
        views.ThesisPublicationYearListView.as_view(),
        name="collection_list_per_year",
    ),
    re_path(
        _(r"^(?P<collection_code>[\w-]+)/(?P<author_letter>[\w\'-])/$"),
        views.ThesisPublicationAuthorNameListView.as_view(),
        name="collection_list_per_author_name",
    ),
    re_path(
        _(r"^citation/(?P<solr_id>.+)\.enw$"),
        views.ThesisEnwCitationView.as_view(),
        name="thesis_citation_enw",
    ),
    re_path(
        _(r"^citation/(?P<solr_id>.+)\.ris$"),
        views.ThesisRisCitationView.as_view(),
        name="thesis_citation_ris",
    ),
    re_path(
        _(r"^citation/(?P<solr_id>.+)\.bib$"),
        views.ThesisBibCitationView.as_view(),
        name="thesis_citation_bib",
    ),
]
