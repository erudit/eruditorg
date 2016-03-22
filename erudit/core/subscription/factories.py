# -*- coding: utf-8 -*-

import factory

from erudit.factories import OrganisationFactory


class PolicyFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'subscription.Policy'

    content_object = factory.SubFactory(OrganisationFactory)
    max_accounts = 10


class InstitutionalAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionalAccount'

    institution = factory.SubFactory(OrganisationFactory)
    policy = factory.SubFactory(PolicyFactory)


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionIPAddressRange'

    institutional_account = factory.SubFactory(InstitutionalAccountFactory)
