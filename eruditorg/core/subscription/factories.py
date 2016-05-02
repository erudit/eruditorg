# -*- coding: utf-8 -*-

import factory

from base.factories import UserFactory

from erudit.factories import JournalFactory
from erudit.factories import OrganisationFactory

from .models import InstitutionIPAddressRange
from .models import JournalAccessSubscription
from .models import JournalManagementPlan
from .models import JournalManagementSubscription


class JournalAccessSubscriptionFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = JournalAccessSubscription


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = InstitutionIPAddressRange


class JournalManagementPlanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JournalManagementPlan


class JournalManagementSubscriptionFactory(factory.django.DjangoModelFactory):
    journal = factory.SubFactory(JournalFactory)
    plan = factory.SubFactory(JournalManagementPlanFactory)

    class Meta:
        model = JournalManagementSubscription
