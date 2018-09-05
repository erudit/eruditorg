from pathlib import Path

import pytest
from django.urls import reverse

from apps.public.book.models import Book


@pytest.fixture(autouse=True)
def use_book_test_fixture(settings):
    settings.BOOKS_DIRECTORY = Path(__file__).parent / 'fixtures'


@pytest.fixture(autouse=True)
def book():
    return Book.objects.create(path='incantation/2018', slug='incant')


@pytest.mark.django_db
def test_books_home_view(client):
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
def test_chapter_view_returns_404_when_chapter_doesnt_exist(client, book):
    response = client.get(reverse('public:book:chapter_detail', kwargs={'slug': book.slug,
                                                                        'chapter_id': 'nochapter'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_chapter_pdf(client, book):
    response = client.get(reverse('public:book:chapter_pdf', kwargs={'slug': book.slug,
                                                                     'chapter_id': '000274li'}))
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
