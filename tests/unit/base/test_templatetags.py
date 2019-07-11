import pytest

from django.urls import resolve
from django.urls import reverse
from django.template import Context
from django.template.base import Template
from django.test import RequestFactory


class TestTransCurrentUrlTag:

    @pytest.mark.parametrize('data, expected_url', (
        ({}, '/en/journals/'),
        ({'foo': 'bar'}, '/en/journals/?foo=bar'),
    ))
    def test_can_translate_a_given_url_in_another_language(self, data, expected_url):
        factory = RequestFactory()
        url = reverse('public:journal:journal_list')
        request = factory.get(url, data=data)
        request.resolver_match = resolve(url)
        template = Template('{% load base_urls_tags %}{% trans_current_url "en" %}')
        context = Context({'request': request})
        rendered = template.render(context)
        assert rendered == expected_url
