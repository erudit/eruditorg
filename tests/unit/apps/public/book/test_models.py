import pytest

from django.core import mail

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


@pytest.mark.django_db
class TestBook:
    @pytest.mark.parametrize("is_published", (True, False))
    def test_email_is_sent_after_book_is_published_or_unpublished(self, is_published):
        book = BookFactory(is_published=is_published)
        book.is_published = not is_published
        book.save()
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ["foo@bar.com", "foo@baz.com"]
