from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from . import views

urlpatterns = [
    url(r'^$', views.BookListView.as_view(), name='home'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/$'), views.BookDetailView.as_view(),
        name='book_detail'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)/$'),
        views.ChapterDetailView.as_view(), name='chapter_detail'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)\.pdf$'),
        views.chapter_pdf_view, name='chapter_pdf'),
]
