from pathlib import Path

import pytest
from django.urls import reverse

from apps.public.book.models import (
    Book,
    BookCollection,
    short_slug,
)

from apps.public.book.test.factories import BookFactory

from waffle.models import Flag


@pytest.fixture
def book():
    collection = BookCollection.objects.create(name='book collection', slug='book-collection')
    return Book.objects.create(collection=collection, title='un book', is_published=True,
                               is_open_access=True, path='fixtures/incantation/2018')


@pytest.fixture(autouse=True)
def use_book_test_fixture(settings):
    settings.BOOKS_DIRECTORY = str(Path(__file__).parent)


@pytest.mark.django_db
def test_books_home_view(client):
    response = client.get(reverse('public:book:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_book_view(client, book):
    url = reverse('public:book:book_detail',
                  kwargs={'collection_slug': book.collection.slug, 'slug': book.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_chapter_view(client, book):
    url = reverse('public:book:chapter_detail',
                  kwargs={'collection_slug': book.collection.slug, 'slug': book.slug,
                          'chapter_id': '000274li'})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_book_view_returns_404_when_book_is_not_published(client):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_home_view_does_not_list_unpublished_books(client):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:home'))
    assert book.slug not in response.content.decode('utf-8')
    assert response.status_code == 200


@pytest.mark.django_db
def test_chapter_view_returns_404_when_book_is_not_publised(client):
    book = BookFactory(is_published=False)
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_chapter_view_returns_404_when_chapter_doesnt_exist(client):
    book = BookFactory()
    response = client.get(reverse('public:book:chapter_detail',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_chapter_pdf(client):
    book = BookFactory()
    response = client.get(reverse('public:book:chapter_pdf',
                                  kwargs={'collection_slug': book.collection.slug,
                                          'slug': book.slug, 'chapter_id': '000274li'}))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'


def test_short_slug_cuts_over_80_chars():
    title = ' '.join(['a'] * 50)
    assert len(short_slug(title, None)) < 80


def test_short_slug_includes_isbn():
    assert short_slug('abc', 'def') == 'abc--def'
