# -*- coding: utf-8 -*-

from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.base import Template
from django.test import RequestFactory
from django.test import TestCase


class TestTransCurrentUrlTag(TestCase):
    def setUp(self):
        super(TestTransCurrentUrlTag, self).setUp()
        self.factory = RequestFactory()
        self.loadstatement = '{% load base_urls_tags %}'

    def test_can_translate_a_given_url_in_another_language(self):
        # Setup
        url = reverse('public:journal:journal_list')
        request = self.factory.get(url)
        request.resolver_match = resolve(url)
        t = Template(self.loadstatement + '{% trans_current_url "en" %}')
        c = Context({'request': request})
        # Run
        rendered = t.render(c)
        # Check
        self.assertEqual(rendered, '/en/revues/')
