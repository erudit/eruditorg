# -*- coding: utf-8 -*-

import factory

from base.factories import UserFactory

from erudit.factories import OrganisationFactory

from .models import InstitutionIPAddressRange
from .models import JournalAccessSubscription


class JournalAccessSubscriptionFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = JournalAccessSubscription


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = InstitutionIPAddressRange
