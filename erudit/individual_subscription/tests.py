from django.test import TestCase

from .factories import OrganizationPolicyFactory, IndividualAccountFactory


class OrganizationPolicyTestCase(TestCase):

    def test_total_accounts(self):
        policy = OrganizationPolicyFactory()
        IndividualAccountFactory(organization_policy=policy)
        IndividualAccountFactory(organization_policy=policy)
        self.assertEqual(policy.total_accounts, 2)
