import datetime
import json
import pytest
import reversion

from django.conf import settings
from django.test import RequestFactory, override_settings
from post_office.models import Email

from apps.userspace.journal.information.forms import JournalInformationForm
from base.test.factories import UserFactory
from erudit.test.factories import JournalInformationFactory


@pytest.mark.django_db
class TestJournalInformationForm:

    def test_can_properly_initialize_form_fields_using_the_passed_language_code(self):
        request = RequestFactory().request()
        request.user = UserFactory()
        form = JournalInformationForm(language_code='en', request=request)
        assert len(form.fields) > 0
        for field in form.get_textbox_fields():
            assert field.name.endswith('_en')


    def test_knows_its_i18n_field_names(self):
        request = RequestFactory().request()
        request.user = UserFactory()
        form = JournalInformationForm(language_code='en', request=request)
        assert len(form.i18n_field_names) > 0
        for fname in form.i18n_field_names:
            assert fname.endswith('_en')


    def test_can_properly_save_i18n_values_on_the_object(self):
        info = JournalInformationFactory.create()
        form_data = {
            'about_en': 'This is a test',
        }
        request = RequestFactory().request()
        request.user = UserFactory()
        form = JournalInformationForm(form_data, instance=info, language_code='en', request=request)
        is_valid = form.is_valid()
        assert is_valid
        info = form.save()
        assert info.about_en == form_data['about_en']

    def test_journal_information_revisions(self):
        user1 = UserFactory()
        user2 = UserFactory()
        with reversion.create_revision():
            info = JournalInformationFactory(about_fr='Premier test')
            reversion.set_user(user1)
            reversion.set_comment('Première révision')
        form_data = {
            'about_fr': 'Deuxième test',
        }
        request = RequestFactory().request()
        request.user = user2
        form = JournalInformationForm(form_data, instance=info, language_code='fr', request=request)
        info = form.save()
        queryset = reversion.models.Version.objects.get_for_object(info)
        current_version = queryset[0]
        previous_version = queryset[1]
        # Check that we have two revision, the initial one and the new one.
        assert queryset.count() == 2
        # Check that the two versions have a different values for the modified field.
        assert json.loads(current_version.serialized_data)[0]['fields']['about_fr'] == info.about_fr
        assert json.loads(previous_version.serialized_data)[0]['fields']['about_fr'] == 'Premier test'
        # Check the revision comments.
        assert current_version.revision.get_comment() == 'Champ(s) modifié(s) : Revue'
        assert previous_version.revision.get_comment() == 'Première révision'
        # Check the revision users.
        assert current_version.revision.user == user2
        assert previous_version.revision.user == user1

    @override_settings(ALLOWED_HOSTS=['www.erudit.org'])
    def test_journal_information_new_revision_notification_email(self):
        with reversion.create_revision():
            info = JournalInformationFactory(
                about_fr='Premier test',
                journal__name='Foobar',
                journal__id=123,
            )
            reversion.set_comment('Première révision')
        form_data = {
            'about_fr': 'Deuxième test',
        }
        request = RequestFactory().request()
        request.META['HTTP_HOST'] = 'www.erudit.org'
        request.user = UserFactory(username='Dougie')
        form = JournalInformationForm(form_data, instance=info, language_code='fr', request=request)
        info = form.save()
        now = datetime.datetime.now()
        email = Email.objects.first()
        # Check that a notification email has been sent to edition@erudit.org.
        assert email.to == [settings.PUBLISHER_EMAIL]
        # Check that the email subject contains the name of the journal.
        assert email.subject == '[Érudit] Nouvelle révision d\'une page "À propos" [Foobar]'
        # Check that the email message contains the diff between the previous revision and the new
        # revision and that it does not include excluded fields (translations & updated).
        assert email.html_message == f"""

<p>Modification faite par <strong>Dougie</strong> le <strong>{now.strftime('%d-%m-%Y')}</strong> à <strong>{now.strftime('%H:%M')}</strong>.</p>

<p>https://www.erudit.org/fr/espace-utilisateur/revue/123/informations/</p>

<h3>Revue [fr]</h3>
<pre class="highlight">
<del>- Premier test</del>
<ins>+ Deuxième test</ins>
</pre>

"""
