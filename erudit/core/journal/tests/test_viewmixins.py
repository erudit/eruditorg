# -*- coding: utf-8 -*-

from django.http import Http404

from core.journal.viewmixins import JournalCodeDetailMixin
from erudit.tests import BaseEruditTestCase


class TestJournalCodeDetailMixin(BaseEruditTestCase):
    def test_can_return_a_journal_based_on_its_code(self):
        # Setup
        code = self.journal.code
        mixin = JournalCodeDetailMixin()
        mixin.kwargs = {'code': code}
        # Run & check
        self.assertEqual(mixin.get_object(), self.journal)

    def test_returns_http_404_if_the_journal_does_not_exist(self):
        # Setup
        code = self.journal.code
        mixin = JournalCodeDetailMixin()
        mixin.kwargs = {'code': code + 'dummy'}
        # Run & check
        with self.assertRaises(Http404):
            mixin.get_object()
