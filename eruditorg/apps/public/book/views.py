from pathlib import Path

from django.conf import settings
from django.db.models import Prefetch
from django.http import (
    HttpResponse,
    Http404,
)
from django.shortcuts import get_object_or_404

from apps.public.book.models import (
    BookCollection,
    Book,
)
from django.views.generic import DetailView, ListView

from apps.public.book.toc import read_toc
from erudit.utils import qs_cache_key


class BookListView(ListView):

    template_name = "public/book/home.html"
    queryset = Book.objects.all().published().top_level().order_by("-year", "title")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = self.get_queryset()

        context["published_books_cache_key"] = qs_cache_key(books)
        context["collections"] = BookCollection.objects.prefetch_related(
            Prefetch("books", queryset=books)
        ).all()

        context["books_count"] = books.count()
        return context


class BookDetailView(DetailView):

    model = Book
    template_name = "public/book/book_detail.html"
    queryset = Book.objects.all().published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.object
        context["toc"] = read_toc(Path(settings.BOOKS_DIRECTORY) / self.object.path)
        return context


class ChapterDetailView(DetailView):

    model = Book
    template_name = "public/book/chapter_detail.html"
    queryset = Book.objects.all().published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["book"] = self.object
        toc = read_toc(Path(settings.BOOKS_DIRECTORY) / self.object.path)
        context["toc"] = toc
        chapter_id = self.kwargs["chapter_id"]
        try:
            context["chapter"] = toc.chapters[chapter_id]
        except KeyError:
            # no chapter with that id in this book
            raise Http404
        context["previous_chapter"] = toc.previous_chapters[chapter_id]
        context["next_chapter"] = toc.next_chapters[chapter_id]
        return context


# noinspection PyUnusedLocal
def chapter_pdf_view(request, collection_slug, slug, chapter_id):
    book = get_object_or_404(Book, slug=slug)
    toc = read_toc(Path(settings.BOOKS_DIRECTORY) / book.path)
    try:
        chapter = toc.chapters[chapter_id]
    except KeyError:
        # no chapter with that id in this book
        raise Http404
    pdf_file = open(str(Path(settings.BOOKS_DIRECTORY) / chapter.pdf_path), "rb")
    response = HttpResponse(content=pdf_file)
    response["Content-Type"] = "application/pdf"
    response["Content-Disposition"] = 'filename="{}.pdf"'.format(chapter_id)
    return response
