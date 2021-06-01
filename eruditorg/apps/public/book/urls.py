from django.urls import re_path
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from . import views

app_name = "book"

urlpatterns = [
    re_path(r"^$", views.BookListView.as_view(), name="home"),
    re_path(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/$"),
        views.BookDetailView.as_view(),
        name="book_detail",
    ),
    re_path(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)/$"),
        views.ChapterDetailView.as_view(),
        name="chapter_detail",
    ),
    re_path(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)\.pdf$"),
        xframe_options_exempt(views.chapter_pdf_view),
        name="chapter_pdf",
    ),
]
