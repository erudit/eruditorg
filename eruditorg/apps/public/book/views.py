from django.views.generic import TemplateView
from erudit.solr.models import get_all_books



class BookListView(TemplateView):

    template_name = "public/book/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['books'] = None
        return context


class BookDetailView(TemplateView):

    template_name = "public/book/book_detail.html"


class ChapterDetailView(TemplateView):

    template_name = "public/book/chapter_detail.html"
