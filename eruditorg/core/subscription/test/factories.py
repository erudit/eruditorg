# -*- coding: utf-8 -*-

import factory

from base.test.factories import UserFactory

from erudit.test.factories import JournalFactory
from erudit.test.factories import OrganisationFactory

from ..models import InstitutionIPAddressRange
from ..models import JournalAccessSubscription
from ..models import JournalAccessSubscriptionPeriod
from ..models import JournalManagementPlan
from ..models import JournalManagementSubscription
from ..models import JournalManagementSubscriptionPeriod


class JournalAccessSubscriptionFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = JournalAccessSubscription


class JournalAccessSubscriptionPeriodFactory(factory.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = JournalAccessSubscriptionPeriod


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


class JournalManagementSubscriptionPeriodFactory(factory.DjangoModelFactory):
    subscription = factory.SubFactory(JournalManagementSubscriptionFactory)

    class Meta:
        model = JournalManagementSubscriptionPeriod
