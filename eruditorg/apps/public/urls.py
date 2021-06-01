# -*- coding: utf-8 -*-

from django.urls import include, re_path
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from . import views
from .journal.urls import journal_urlpatterns

public_urlpatterns = (
    [
        re_path(r"^$", views.HomeView.as_view(), name="home"),
        re_path(_(r"^compte/"), include("apps.public.auth.urls")),
        re_path(
            _(r"^compte/actions/"),
            include("apps.public.account_actions.urls", namespace="account_actions"),
        ),
        re_path(_(r"^notices/"), include("apps.public.citations.urls", namespace="citations")),
        re_path(_(r"^recherche/"), include("apps.public.search.urls", namespace="search")),
        re_path(_(r"^theses/"), include("apps.public.thesis.urls", namespace="thesis")),
        re_path(_(r"^livres/"), include("apps.public.book.urls", namespace="book")),
        re_path(
            _(r"^identite/$"),
            TemplateView.as_view(template_name="public/brand_assets.html"),
            name="brand_assets",
        ),
        re_path(
            _(r"^20ans/$"),
            TemplateView.as_view(template_name="public/20_years.html"),
            name="20_years",
        ),
        # The journal URLs are at the end of the list because some of them are catchalls.
        re_path(r"^", include(journal_urlpatterns)),
    ],
    "public",
)
