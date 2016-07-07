# -*- coding: utf-8 -*-

from django.contrib.auth.models import User

from django.test import TestCase

from core.accounts.models import LegacyAccountProfile
from core.accounts.utils.mandragore import can_create_mandragore_user
from core.accounts.utils.mandragore import create_mandragore_profile_for_user
from core.accounts.utils.mandragore import create_or_update_mandragore_user
from core.accounts.utils.mandragore import get_list_as_sql
from core.accounts.utils.mandragore import get_mandragore_user
from core.accounts.utils.mandragore import MandragoreError
from core.accounts.utils.mandragore import user_coherent_with_mandragore


class TestCommands(TestCase):
    def setUp(self):
        super(TestCommands, self).setUp()
        self.user = User.objects.create_user(
            username='foobar',
            email='foobar@erudit.org',
            password='top_secret'
        )

    def test_create_mandragore_profile_for_user(self):

        mandragore_profile = create_mandragore_profile_for_user(
            9001, self.user
        )

        self.assertTrue(
            mandragore_profile.synced_with_origin
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
        mandragoreprofile = LegacyAccountProfile.objects \
            .filter(origin=LegacyAccountProfile.DB_MANDRAGORE, user=user).first()

        self.assertIsNotNone(
            mandragoreprofile
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
