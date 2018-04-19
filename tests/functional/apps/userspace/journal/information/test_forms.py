import pytest
from erudit.test.factories import JournalInformationFactory

from apps.userspace.journal.information.forms import JournalInformationForm


def test_can_properly_initialize_form_fields_using_the_passed_language_code():
    form = JournalInformationForm(language_code='en')
    assert len(form.fields) > 0
    for field in form.get_textbox_fields():
        assert field.name.endswith('_en')


def test_knows_its_i18n_field_names():
    form = JournalInformationForm(language_code='en')
    assert len(form.i18n_field_names) > 0
    for fname in form.i18n_field_names:
        assert fname.endswith('_en')


@pytest.mark.django_db
def test_can_properly_save_i18n_values_on_the_object():
    info = JournalInformationFactory.create()
    form_data = {
        'about_en': 'This is a test',
    }
    form = JournalInformationForm(form_data, instance=info, language_code='en')
    is_valid = form.is_valid()
    assert is_valid
    info = form.save()
    assert info.about_en == form_data['about_en']
