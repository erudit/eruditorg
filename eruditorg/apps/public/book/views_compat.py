from django.urls import reverse
from django.views.generic import RedirectView

from apps.public.book.models import (
    BookCollection,
    Book,
)
from base.viewmixins import ActivateLegacyLanguageViewMixin


class BooksHomeRedirectView(
    ActivateLegacyLanguageViewMixin,
    RedirectView
):
    pattern_name = 'public:book:home'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        return super().get_redirect_url()


class CollectionRedirectView(
    ActivateLegacyLanguageViewMixin,
    RedirectView
):
    pattern_name = 'public:book:home'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        url = super().get_redirect_url()
        path = 'livre/{}'.format(kwargs['collection'])
        collection = BookCollection.objects.get(path=path)
        return '{}#{}'.format(url, collection.slug)


class BookRedirectView(
    ActivateLegacyLanguageViewMixin,
    RedirectView
):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        path = 'livre/{}/{}'.format(kwargs['collection'], kwargs['book'])
        book = Book.objects.get(path=path)
        return reverse('public:book:book_detail', kwargs={'collection_slug': book.collection.slug,
                                                          'slug': book.slug})


class ChapterRedirectView(ActivateLegacyLanguageViewMixin, RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        path = 'livre/{}/{}'.format(kwargs['collection'], kwargs['book'])
        book = Book.objects.get(path=path)
        view_name = 'chapter_pdf' if 'pdf' in kwargs else 'chapter_detail'
        return reverse(f'public:book:{view_name}', kwargs={
            'collection_slug': book.collection.slug,
            'slug': book.slug,
            'chapter_id': kwargs['chapter_id'],
        })
