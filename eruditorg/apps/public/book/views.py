from pathlib import Path

from django.conf import settings
from django.http import (
    HttpResponse,
    Http404,
)
from django.shortcuts import get_object_or_404

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
        context['books'] = Book.objects.all()
        return context


class BookDetailView(DetailView):

    model = Book
    template_name = "public/book/book_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object
        context['toc'] = read_toc(Path(settings.BOOKS_DIRECTORY) / self.object.path)
        return context


class ChapterDetailView(DetailView):

    model = Book
    template_name = "public/book/chapter_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book'] = self.object
        toc = read_toc(Path(settings.BOOKS_DIRECTORY) / self.object.path)
        context['toc'] = toc
        chapter_id = self.kwargs['chapter_id']
        try:
            context['chapter'] = toc.chapters[chapter_id]
        except KeyError:
            # no chapter with that id in this book
            raise Http404
        context['previous_chapter'] = toc.previous_chapters[chapter_id]
        context['next_chapter'] = toc.next_chapters[chapter_id]
        return context


def chapter_pdf_view(request, slug, chapter_id):
    book = get_object_or_404(Book, slug=slug)
    toc = read_toc(Path(settings.BOOKS_DIRECTORY) / book.path)
    try:
        chapter = toc.chapters[chapter_id]
    except KeyError:
        # no chapter with that id in this book
        raise Http404
    pdf_file = open(str(Path(settings.BOOKS_DIRECTORY) / chapter.pdf_path), 'rb')
    response = HttpResponse(content=pdf_file)
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(chapter_id)
    return response
