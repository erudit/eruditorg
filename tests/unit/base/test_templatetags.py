# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.files import File
from django.core.urlresolvers import resolve
from django.core.urlresolvers import reverse
from django.template import Context
from django.template.base import Template
from django.test import RequestFactory
import pytest


class TestTransCurrentUrlTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
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
        assert rendered == '/en/revues/'


class TestFilenameFilterTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()
        self.loadstatement = '{% load base_file_tags %}'

    def test_can_return_the_name_of_a_file(self):
        # Setup
        url = reverse('public:journal:journal_list')
        request = self.factory.get(url)
        request.resolver_match = resolve(url)
        t = Template(self.loadstatement + '{{ f|filename }}')
        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + '/200x200.png', 'rb')
        df = File(f)
        c = Context({'request': request, 'f': df})
        # Run
        rendered = t.render(c)
        # Check
        assert rendered == '200x200.png'
        df.close()
        f.close()


class TestMimetypeFilterTag(object):
    @pytest.fixture(autouse=True)
    def setup(self):
        self.factory = RequestFactory()
        self.loadstatement = '{% load base_file_tags %}'

    def test_can_return_the_name_of_a_file(self):
        # Setup
        url = reverse('public:journal:journal_list')
        request = self.factory.get(url)
        request.resolver_match = resolve(url)
        t = Template(self.loadstatement + '{{ f|mimetype }}')
        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + '/200x200.png', 'rb')
        df = File(f)
        c = Context({'request': request, 'f': df})
        # Run
        rendered = t.render(c)
        # Check
        assert rendered == 'image/png'
        df.close()
        f.close()
