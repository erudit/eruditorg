# -*- coding: utf-8 -*-
import datetime as dt

import factory
import factory.fuzzy

from base.test.factories import UserFactory

from erudit.test.factories import JournalFactory
from erudit.test.factories import OrganisationFactory

from ..models import InstitutionIPAddressRange
from ..models import JournalAccessSubscription
from ..models import JournalAccessSubscriptionPeriod
from ..models import JournalManagementPlan
from ..models import JournalManagementSubscription
from ..models import JournalManagementSubscriptionPeriod
from ..models import InstitutionReferer
from ..models import AccessBasket


class AccessBasketFactory(factory.DjangoModelFactory):
    name = "some name"

    class Meta:
        model = AccessBasket

    @factory.post_generation
    def journals(obj, created, extracted, **kwargs):
        if extracted:
            for journal in extracted:
                obj.journals.add(journal)


class JournalAccessSubscriptionFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = JournalAccessSubscription

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):
        if kwargs.get('valid', False):
            ValidJournalAccessSubscriptionPeriodFactory(subscription=obj)
        if kwargs.get('referers', None):
            for referer in kwargs.get('referers'):
                InstitutionRefererFactory(
                    subscription=obj,
                    referer=referer
                )
        ip_start = kwargs.get('ip_start', None)
        ip_end = kwargs.get('ip_end', None)
        if ip_start and ip_end:
            InstitutionIPAddressRangeFactory(
                ip_start=ip_start,
                ip_end=ip_end,
                subscription=obj
            )
        journals = kwargs.get('journals')
        if journals:
            obj.journal = journals[0]
            obj.journal_management_subscription = JournalManagementSubscription.objects \
                .filter(journal=journals[0]).first()
            for journal in journals:
                obj.journals.add(journal)
            obj.save()

    @factory.post_generation
    def type(obj, create, extracted, **kwargs):
        if extracted == 'individual':
            obj.organisation = None
            obj.save()

    @factory.post_generation
    def journal(obj, create, extracted, **kwargs):
        if extracted is not None:
            obj.journal = extracted
            obj.journal_management_subscription = JournalManagementSubscription.objects \
                .filter(journal=extracted).first()

    @factory.post_generation
    def valid(obj, create, extracted, **kwargs):
        if extracted:
            ValidJournalAccessSubscriptionPeriodFactory(subscription=obj)

    @factory.post_generation
    def expired(obj, create, extracted, **kwargs):
        if extracted:
            ExpiredJournalAccessSubscriptionPeriodFactory(subscription=obj)


class JournalAccessSubscriptionPeriodFactory(factory.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = JournalAccessSubscriptionPeriod


class ValidJournalAccessSubscriptionPeriodFactory(JournalAccessSubscriptionPeriodFactory):

    start = dt.datetime.now() - dt.timedelta(days=10)
    end = dt.datetime.now() + dt.timedelta(days=10)


class ExpiredJournalAccessSubscriptionPeriodFactory(JournalAccessSubscriptionPeriodFactory):

    start = dt.datetime.now() - dt.timedelta(days=10)
    end = dt.datetime.now() - dt.timedelta(days=5)


class InstitutionRefererFactory(factory.DjangoModelFactory):

    subscription = factory.SubFactory(ValidJournalAccessSubscriptionPeriodFactory)

    class Meta:
        model = InstitutionReferer


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = InstitutionIPAddressRange


class JournalManagementPlanFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: 'plan{}'.format(n))
    max_accounts = 5

    class Meta:
        model = JournalManagementPlan


class JournalManagementSubscriptionFactory(factory.django.DjangoModelFactory):
    journal = factory.SubFactory(JournalFactory)
    plan = factory.SubFactory(JournalManagementPlanFactory)

    class Meta:
        model = JournalManagementSubscription

    @factory.post_generation
    def valid(obj, create, extracted, **kwargs):
        if extracted:
            JournalManagementSubscriptionPeriodFactory(
                subscription=obj,
                start=dt.datetime.now() - dt.timedelta(days=10),
                end=dt.datetime.now() + dt.timedelta(days=10))

    @factory.post_generation
    def expired(obj, create, extracted, **kwargs):
        if extracted:
            JournalManagementSubscriptionPeriodFactory(
                subscription=obj,
                start=dt.datetime.now() - dt.timedelta(days=10),
                end=dt.datetime.now() - dt.timedelta(days=5))


class JournalManagementSubscriptionPeriodFactory(factory.DjangoModelFactory):
    subscription = factory.SubFactory(JournalManagementSubscriptionFactory)

    class Meta:
        model = JournalManagementSubscriptionPeriod
