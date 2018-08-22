from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from . import views

urlpatterns = [
    url(r'^$', views.BookListView.as_view(), name='home'),
    url(_(r'^livre/(?P<slug>[-\w]+)/(?P<pk>[0-9]+)/$'), views.BookDetailView.as_view(),
        name='book_detail'),
    url(_(r'^chapitre/(?P<slug>[-\w]+)/(?P<pk>[0-9]+)/(?P<chapter_id>[\w]+)/$'),
        views.ChapterDetailView.as_view(), name='chapter_detail'),
    url(_(r'^chapitre/(?P<slug>[-\w]+)/(?P<pk>[0-9]+)/(?P<chapter_id>[\w]+)/pdf$'),
        views.chapter_pdf_view, name='chapter_pdf'),
]
