from pathlib import Path

from django.conf import settings

from apps.public.book.models import (
    BookCollection,
    Book,
)
from django.views.generic import (
    TemplateView,
    DetailView,
)

from apps.public.book.toc import read_toc


class BookListView(TemplateView):

    template_name = "public/book/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collections'] = BookCollection.objects.all()
        return context


class BookDetailView(DetailView):

    model = Book
    template_name = "public/book/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object
        context['toc'] = read_toc(Path(settings.BOOKS_DIRECTORY) / self.object.path)
        return context


class ChapterDetailView(TemplateView):

    template_name = "public/book/chapter_detail.html"
