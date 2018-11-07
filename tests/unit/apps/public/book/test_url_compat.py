from django.http import HttpResponsePermanentRedirect

import pytest

from apps.public.book.models import (
    BookCollection,
    Book,
)


@pytest.mark.django_db
def test_home_redirect(client):
    response = client.get('/livre/')
    assert isinstance(response, HttpResponsePermanentRedirect)
    assert response.url == '/fr/livres/'


@pytest.mark.django_db
def test_collection_redirect(client):
    BookCollection.objects.create(slug='collection-slug', path='livre/collectionpath')
    response = client.get('/livre/collectionpath/index.htm')
    assert isinstance(response, HttpResponsePermanentRedirect)
    assert response.url == '/fr/livres/#collection-slug'


@pytest.mark.django_db
def test_book_redirect(client):
    collection = BookCollection.objects.create(name='hors collection', slug='hors-collection')
    Book.objects.create(path='livre/collectionpath/bookpath', collection=collection,
                        title='le book')
    response = client.get('/livre/collectionpath/bookpath/index.htm')
    assert isinstance(response, HttpResponsePermanentRedirect)
    assert response.url == '/fr/livres/hors-collection/book/'

