# -*- coding: utf-8 -*-

from erudit.tests import BaseEruditTestCase

from erudit.factories import JournalInformationFactory

from ..forms import JournalInformationForm


class TestJournalInformationForm(BaseEruditTestCase):
    def test_can_properly_initialize_form_fields_using_the_passed_language_code(self):
        # Run & check
        form = JournalInformationForm(language_code='en')
        self.assertTrue(len(form.fields))
        for fname in form.fields:
            self.assertTrue(fname.endswith('_en'))

    def test_knows_its_i18n_field_names(self):
        # Run & check
        form = JournalInformationForm(language_code='en')
        self.assertTrue(len(form.i18n_field_names))
        for fname in form.i18n_field_names:
            self.assertTrue(fname.endswith('_en'))

    def test_can_properly_save_i18n_values_on_the_object(self):
        # Setup
        info = JournalInformationFactory.create(journal=self.journal)
        form_data = {
            'about_en': 'This is a test',
        }
        # Run & check
        form = JournalInformationForm(form_data, instance=info, language_code='en')
        is_valid = form.is_valid()
        self.assertTrue(is_valid)
        info = form.save()
        self.assertEqual(info.about_en, form_data['about_en'])
