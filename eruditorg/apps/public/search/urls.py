from django.urls import re_path
from django.utils.translation import gettext_lazy as _

from . import views

app_name = "search"

urlpatterns = [
    re_path(r"^$", views.SearchResultsView.as_view(), name="results"),
    re_path(r"^avancee/$", views.AdvancedSearchView.as_view(), name="advanced_search"),
    re_path(_(r"^sauvegardes/ajout/$"), views.SavedSearchAddView.as_view(), name="add_search"),
    re_path(
        _(r"^sauvegardes/suppression/(?P<uuid>[\w-]+)/$"),
        views.SavedSearchRemoveView.as_view(),
        name="remove_search",
    ),
]
