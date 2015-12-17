from django.test import TestCase

from .factories import OrganizationPolicyFactory, IndividualAccountFactory


class OrganizationPolicyTestCase(TestCase):

    def test_total_accounts(self):
        policy = OrganizationPolicyFactory()
        IndividualAccountFactory(organization_policy=policy)
        IndividualAccountFactory(organization_policy=policy)
        self.assertEqual(policy.total_accounts, 2)

    def test_date_activation(self):
        policy = OrganizationPolicyFactory()
        self.assertIsNone(policy.date_activation)

        IndividualAccountFactory(organization_policy=policy)
        self.assertIsNotNone(policy.date_activation)

        first_date_activation = policy.date_activation
        IndividualAccountFactory(organization_policy=policy)
        self.assertEqual(policy.date_activation, first_date_activation)
