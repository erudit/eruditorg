from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from . import views
from waffle.decorators import waffle_flag

app_name = "book"

urlpatterns = [
    url(r'^$',
        waffle_flag('BOOKS')(
            views.BookListView.as_view()
        ), name='home'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/$'),
        waffle_flag('BOOKS')(views.BookDetailView.as_view()),
        name='book_detail'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)/$'),
        waffle_flag('BOOKS')(views.ChapterDetailView.as_view()), name='chapter_detail'),
    url(_(r'^(?P<collection_slug>[-\w]+)/(?P<slug>[-\w]+)/(?P<chapter_id>[a-z0-9]+)\.pdf$'),
        waffle_flag('BOOKS')(views.chapter_pdf_view), name='chapter_pdf'),
]
