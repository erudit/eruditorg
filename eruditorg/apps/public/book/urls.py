from django.conf.urls import url
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt
from . import views

app_name = "book"

urlpatterns = [
    url(r"^$", views.BookListView.as_view(), name="home"),
    url(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/$"),
        views.BookDetailView.as_view(),
        name="book_detail",
    ),
    url(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)/$"),
        views.ChapterDetailView.as_view(),
        name="chapter_detail",
    ),
    url(
        _(r"^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)\.pdf$"),
        xframe_options_exempt(views.chapter_pdf_view),
        name="chapter_pdf",
    ),
]
