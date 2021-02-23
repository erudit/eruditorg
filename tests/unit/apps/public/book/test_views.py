import pytest

from apps.public.book.test.factories import BookCollectionFactory, BookFactory
from apps.public.book.views import BookListView


@pytest.mark.django_db
class TestBookListView:
    def test_books_order(self):
        collection = BookCollectionFactory()
        book_1 = BookFactory(collection=collection, year="2000", title="A")
        book_2 = BookFactory(collection=collection, year="2000", title="B")
        book_3 = BookFactory(collection=collection, year="2002", title="D")
        book_4 = BookFactory(collection=collection, year="2001", title="C")
        view = BookListView()
        view.object_list = None
        context = view.get_context_data()
        assert list(context["collections"][0].books.all()) == [book_3, book_4, book_1, book_2]
