# -*- coding: utf-8 -*-

from erudit.test import BaseEruditTestCase

from ..templatetags.public_search_tags import highlight


class TestHighlightFilterTag(BaseEruditTestCase):
    def test_can_highlight_a_text_using_a_word(self):
        # Setup
        text = 'Test foo bar'
        # Run & check
        output = highlight(text, 'foo')
        self.assertEqual(output, 'Test <mark class="highlight">foo</mark> bar')

    def test_do_nothing_if_the_word_is_null(self):
        # Setup
        text = 'Test foo bar'
        # Run & check
        output = highlight(text, '')
        self.assertEqual(output, 'Test foo bar')
