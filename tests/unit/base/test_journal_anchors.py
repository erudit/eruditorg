import pytest
from django.http import HttpResponseRedirect


@pytest.mark.django_db
def test_can_redirect_canonical_url_when_language_is_default(client):
    response = client.get('/revues/images/2018-n186-images03609/')
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/fr/revues/images/2018-n186-images03609/'


@pytest.mark.django_db
def test_can_redirect_canonical_url_when_language_is_supported_but_not_default(client):
    response = client.get('/revues/images/2018-n186-images03609/', HTTP_ACCEPT_LANGUAGE='en')
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/en/journals/images/2018-n186-images03609/'


@pytest.mark.django_db
def test_can_redirect_canonical_url_when_language_is_not_supported(client):
    response = client.get('/revues/images/2018-n186-images03609/', HTTP_ACCEPT_LANGUAGE='de')
    assert isinstance(response, HttpResponseRedirect)
    assert response.url == '/fr/revues/images/2018-n186-images03609/'
