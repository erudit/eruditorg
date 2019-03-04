import pytest

from apps.public.book.models import Book
from apps.public.book.test.factories import BookFactory


@pytest.mark.django_db
class TestBookQueryset:

    def test_published_sub_book_is_published_if_parent_is_published(self):
        book = BookFactory(is_published=True)
        sub_book = BookFactory(parent_book=book)
        assert Book.objects.all().published().count() == 2

    def test_top_level_filters_all_subbooks(self):
        book = BookFactory(is_published=True)
        sub_book = BookFactory(parent_book=book)
        assert Book.objects.all().published().top_level().count() == 1
        assert Book.objects.all().published().top_level().first().pk == book.pk
