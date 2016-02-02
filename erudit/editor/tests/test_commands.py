# from datetime import datetime
from django.contrib.auth.models import User

from erudit.models import Publisher

from editor.tests.base import BaseEditorTestCase
from erudit.utils.mandragore import (
    create_mandragore_profile_for_user,
    user_coherent_with_mandragore,
    can_create_mandragore_user,
    get_list_as_sql,
    create_or_update_mandragore_user,
    MandragoreError,
    get_mandragore_user
)

from erudit.utils.edinum import (
    create_or_update_publisher,
    create_or_update_journal
)

from erudit.factories import JournalFactory, PublisherFactory


class TestCommands(BaseEditorTestCase):

    def test_create_mandragore_profile_for_user(self):

        mandragore_profile = create_mandragore_profile_for_user(
            9001, self.user
        )

        self.assertTrue(
            mandragore_profile.synced_with_mandragore
        )

    def test_user_coherent_with_mandragore(self):

        # Create a fake mandragore user

        mandragore_user = User(
            first_name="Karl",
            last_name="Marx",
            username="kmarx",
            email="kmarx@international.info",
        )

        mandragore_user.save()

        mandragoreprofile = create_mandragore_profile_for_user(
            '1234',
            mandragore_user
        )
        mandragoreprofile.save()

        self.assertTrue(
            user_coherent_with_mandragore(
                mandragore_user,
                {
                    'person_id': '1234',
                    'username': 'kmarx',
                    'email': 'kmarx@international.info',
                }
            )
        )

    def test_can_create_mandragore_user(self):

        self.assertTrue(
            can_create_mandragore_user(
                "new username !!",
                "dummy mandragore id!",
            ),
            "We should be able to create a mandragore user for a nonexistent username and nonexistent mandragore id"  # noqa
        )

        self.assertFalse(
            can_create_mandragore_user(
                self.user.username,
                "dummy mandragore id!",
            ),
            "We should not be able to create a mandragore user for an existing username"
        )

        create_mandragore_profile_for_user("12345", self.user)

        self.assertFalse(
            can_create_mandragore_user(
                "dummy user",
                "12345"
            ),
            "We should not be able to create a mandragore user for an existing mandragore id"
        )

    def test_get_list_as_sql(self):
        self.assertEquals(
            get_list_as_sql([1, 2]),
            '"1","2"'
        )

    def test_create_or_update_mandragore_user(self):

        user = create_or_update_mandragore_user(
            '1234', username="fengels", first_name="Friedrich", last_name="Engels"
        )

        self.assertIsNotNone(
            user.mandragoreprofile
        )

        self.assertEquals(
            user.first_name,
            "Friedrich"
        )

        user = create_or_update_mandragore_user(
            '1234', username="fengels", first_name="updated"
        )

        self.assertEquals(
            user.first_name,
            "updated"
        )

        with self.assertRaises(MandragoreError):
            create_or_update_mandragore_user(
                'bad id', username="fengels", last_name="updated"
            )

    def test_get_mandragore_user(self):

        # A user with no profile should raise the error
        with self.assertRaises(MandragoreError):
            get_mandragore_user(self.user.username)

        create_mandragore_profile_for_user("1234", self.user)

        # Validating with a different person_id should raise the error
        with self.assertRaises(MandragoreError):
            get_mandragore_user(self.user.username, person_id="123456")

        user = get_mandragore_user(self.user.username, person_id="1234")
        self.assertEquals(
            user.pk,
            self.user.pk
        )

    def test_create_or_update_publisher(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        self.assertEquals(publisher.name, "dcormier")
        self.assertEquals(publisher.edinum_id, "123456")

        publisher_2 = create_or_update_publisher("123456", "dcormier2")
        self.assertEquals(publisher_2.pk, publisher.pk)
        self.assertEquals(publisher_2.name, "dcormier2")

        # create another publisher with the same edinum_id
        Publisher.objects.create(name="bob", edinum_id="123456")
        publisher = create_or_update_publisher("123456", "dcormier2")
        self.assertIsNone(publisher)

    def test_can_create_journal_and_publisher(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        journal = create_or_update_journal(
            publisher, "123", "Journal of journals", "joj", "", ""
        )

        self.assertEquals(
            journal.edinum_id, "123"
        )

    def test_can_update_journal(self):
        publisher = create_or_update_publisher("123456", "dcormier")
        journal = create_or_update_journal(
            publisher, "123", "Journal of journals", "joj", "", ""
        )

        self.assertEquals(
            journal.edinum_id, "123"
        )

        journal_2 = create_or_update_journal(
            publisher, "123", "Journal", "joj", "", ""
        )

        self.assertEquals(
            journal.pk,
            journal_2.pk
        )

        self.assertEquals(
            journal_2.name,
            "Journal"
        )

    def test_cannot_create_journal_if_nonedinum_journal_exists(self):
        # create another journal with the same edinum_id
        publisher = PublisherFactory.create()

        journal = JournalFactory.create(edinum_id="123", publishers=[publisher])

        journal = create_or_update_journal(
            publisher, "123", "test", "testj", "", ""
        )

        self.assertIsNone(journal)
