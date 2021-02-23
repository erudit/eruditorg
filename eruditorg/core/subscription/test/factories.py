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


class AccessBasketFactory(factory.django.DjangoModelFactory):
    name = "some name"

    class Meta:
        model = AccessBasket

    @factory.post_generation
    def journals(obj, created, extracted, **kwargs):
        if extracted:
            for journal in extracted:
                obj.journals.add(journal)


class JournalAccessSubscriptionFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)

    class Meta:
        model = JournalAccessSubscription

    @factory.post_generation
    def post(obj, create, extracted, **kwargs):

        if kwargs.get("valid", False):
            ValidJournalAccessSubscriptionPeriodFactory(subscription=obj)
            journal = JournalFactory()
            obj.journals.add(journal)
            obj.save()
        if kwargs.get("referers", None):
            for referer in kwargs.get("referers"):
                InstitutionRefererFactory(subscription=obj, referer=referer)
        ip_start = kwargs.get("ip_start", None)
        ip_end = kwargs.get("ip_end", None)
        if ip_start and ip_end:
            InstitutionIPAddressRangeFactory(ip_start=ip_start, ip_end=ip_end, subscription=obj)
        journals = kwargs.get("journals")
        if journals:
            obj.journals.set(journals)
            obj.journal_management_subscription = JournalManagementSubscription.objects.filter(
                journal=journals[0]
            ).first()
            obj.save()

    @factory.post_generation
    def type(obj, create, extracted, **kwargs):

        if extracted == "individual":
            # FIXME individual subscriptions are not linked to an organisations. Rather, they
            # are linked to a JournalManagementSubscription. Because the organisation is created
            # through a SubFactory, and because many tests rely on this behaviour, we set the
            # organistion to None and delete the related object when we create individual
            # individual subscriptions. A proper fix would be to remove the SubFactory and specify
            # the organisation in a post hook.
            organisation = obj.organisation
            obj.organisation = None
            organisation.delete()

            # Only set the journal management subscription if it has not been set. User may want
            # to specify this themselves.
            if not obj.journal_management_subscription:
                obj.journal_management_subscription = JournalManagementSubscriptionFactory()
                obj.journal_management_subscription.save()
                obj.journals.add(obj.journal_management_subscription.journal)
            obj.save()

    @factory.post_generation
    def journals(obj, create, extracted, **kwargs):
        if extracted:
            for journal in extracted:
                obj.journals.add(journal)
                obj.journal_management_subscription = JournalManagementSubscription.objects.filter(
                    journal=journal
                ).first()

    @factory.post_generation
    def valid(obj, create, extracted, **kwargs):
        if extracted:
            if obj.journal_management_subscription is not None:
                ValidJournalManagementSubscriptionPeriodFactory(
                    subscription=obj.journal_management_subscription
                )
            period = ValidJournalAccessSubscriptionPeriodFactory(subscription=obj)
            period.save()

    @factory.post_generation
    def expired(obj, create, extracted, **kwargs):
        if extracted:
            ExpiredJournalAccessSubscriptionPeriodFactory(subscription=obj)


class JournalAccessSubscriptionPeriodFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = JournalAccessSubscriptionPeriod


class ValidJournalAccessSubscriptionPeriodFactory(JournalAccessSubscriptionPeriodFactory):

    start = dt.datetime.now() - dt.timedelta(days=10)
    end = dt.datetime.now() + dt.timedelta(days=10)


class ExpiredJournalAccessSubscriptionPeriodFactory(JournalAccessSubscriptionPeriodFactory):

    start = dt.datetime.now() - dt.timedelta(days=10)
    end = dt.datetime.now() - dt.timedelta(days=5)


class InstitutionRefererFactory(factory.django.DjangoModelFactory):

    subscription = factory.SubFactory(ValidJournalAccessSubscriptionPeriodFactory)

    class Meta:
        model = InstitutionReferer


class InstitutionIPAddressRangeFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalAccessSubscriptionFactory)

    class Meta:
        model = InstitutionIPAddressRange


class JournalManagementPlanFactory(factory.django.DjangoModelFactory):
    code = factory.Sequence(lambda n: "plan{}".format(n))
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
                end=dt.datetime.now() + dt.timedelta(days=10),
            )

    @factory.post_generation
    def expired(obj, create, extracted, **kwargs):
        if extracted:
            JournalManagementSubscriptionPeriodFactory(
                subscription=obj,
                start=dt.datetime.now() - dt.timedelta(days=10),
                end=dt.datetime.now() - dt.timedelta(days=5),
            )


class JournalManagementSubscriptionPeriodFactory(factory.django.DjangoModelFactory):
    subscription = factory.SubFactory(JournalManagementSubscriptionFactory)

    class Meta:
        model = JournalManagementSubscriptionPeriod


class ValidJournalManagementSubscriptionPeriodFactory(JournalManagementSubscriptionPeriodFactory):

    start = dt.datetime.now() - dt.timedelta(days=10)
    end = dt.datetime.now() + dt.timedelta(days=10)
