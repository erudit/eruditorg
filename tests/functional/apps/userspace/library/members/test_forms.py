from account_actions.models import AccountActionToken
from account_actions.test.factories import AccountActionTokenFactory
from django.test import TestCase
from faker import Factory

from base.test.factories import UserFactory
from erudit.test.factories import OrganisationFactory

from core.journal.account_actions import OrganisationMembershipAction

from apps.userspace.library.members.forms import OrganisationMembershipTokenCreateForm

faker = Factory.create()


class TestOrganisationMembershipTokenCreateForm(TestCase):
    def setUp(self):
        super(TestOrganisationMembershipTokenCreateForm, self).setUp()
        self.organisation = OrganisationFactory.create()

    def test_can_validate_a_basic_membership_token(self):
        # Setup
        form_data = {
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }
        form = OrganisationMembershipTokenCreateForm(form_data, organisation=self.organisation)
        # Run & check
        self.assertTrue(form.is_valid())

    def test_cannot_validate_if_the_email_is_already_used_by_another_token(self):
        # Setup
        AccountActionTokenFactory.create(
            action=OrganisationMembershipAction.name,
            content_object=self.organisation,
            email="foo@example.com",
        )
        form_data = {
            "email": "foo@example.com",
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }
        form = OrganisationMembershipTokenCreateForm(form_data, organisation=self.organisation)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue("email" in form.errors)

    def test_cannot_validate_if_the_email_is_already_used_by_a_member_of_the_organisation(self):
        # Setup
        user = UserFactory()
        self.organisation.members.add(user)
        form_data = {
            "email": user.email,
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }
        form = OrganisationMembershipTokenCreateForm(form_data, organisation=self.organisation)
        # Run & check
        self.assertFalse(form.is_valid())
        self.assertTrue("email" in form.errors)

    def test_can_properly_create_a_membership_token(self):
        # Setup
        form_data = {
            "email": faker.email(),
            "first_name": faker.first_name(),
            "last_name": faker.last_name(),
        }
        form = OrganisationMembershipTokenCreateForm(form_data, organisation=self.organisation)
        # Run & check
        self.assertTrue(form.is_valid())
        form.save()
        token = AccountActionToken.objects.first()
        self.assertEqual(token.email, form_data["email"])
        self.assertEqual(token.first_name, form_data["first_name"])
        self.assertEqual(token.last_name, form_data["last_name"])
        self.assertEqual(token.action, OrganisationMembershipAction.name)
        self.assertTrue(token.can_be_consumed)
