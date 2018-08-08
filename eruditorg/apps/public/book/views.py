from apps.public.book.models import BookCollection
from django.views.generic import TemplateView


class BookListView(TemplateView):

    template_name = "public/book/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['collections'] = BookCollection.objects.all()
        return context


class BookDetailView(TemplateView):

    template_name = "public/book/book_detail.html"


class ChapterDetailView(TemplateView):

    template_name = "public/book/chapter_detail.html"
