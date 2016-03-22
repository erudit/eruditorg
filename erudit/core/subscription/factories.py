# -*- coding: utf-8 -*-

import factory

from erudit.factories import OrganisationFactory


class InstitutionalAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionalAccount'

    institution = factory.SubFactory(OrganisationFactory)


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'subscription.InstitutionIPAddressRange'

    institutional_account = factory.SubFactory(InstitutionalAccountFactory)
