from pathlib import Path

import pytest
from django.urls import reverse

from apps.public.book.models import (
    Book,
    BookCollection,
)

from apps.public.book.test.factories import BookCollectionFactory, BookFactory

from waffle.models import Flag

@pytest.fixture
def book_flag():
    Flag.objects.get_or_create(name='BOOKS', everyone=True)


@pytest.fixture(autouse=True)
def use_book_test_fixture(settings):
    settings.BOOKS_DIRECTORY = Path(__file__).parent


@pytest.mark.django_db
def test_books_home_view(client, book_flag):
    response = client.get(reverse('public:book:home'))
    assert response.status_code == 200

# Uncomment when templates are ready
# @pytest.mark.django_db
# def test_book_view(client, book):
#     response = client.get(reverse('public:book:book_detail', kwargs={'slug': book.slug}))
#     assert response.status_code == 200
#
#
# @pytest.mark.django_db
# def test_chapter_view(client, book):
#     response = client.get(reverse('public:book:chapter_detail', kwargs={'slug': book.slug,
#                                                                        'chapter_id': '000274li'}))
#     assert response.status_code == 200
#
#

@pytest.mark.django_db
def test_book_view_returns_404_when_book_is_not_published(client, book_flag):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_view_does_not_list_unpublished_books(client, book_flag):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:home'))
    assert book.slug not in response.content.decode('utf-8')
    assert response.status_code == 200


@pytest.mark.django_db
def test_chapter_view_returns_404_when_book_is_not_publised(client, book_flag):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_chapter_view_returns_404_when_chapter_doesnt_exist(client, book_flag):
    book = BookFactory()
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_chapter_pdf(client, book_flag):
    book = BookFactory()
    response = client.get(reverse('public:book:chapter_pdf',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': '000274li'}))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
