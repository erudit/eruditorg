# -*- coding: utf-8 -*-


from core.subscription.models import JournalAccessSubscription, JournalAccessSubscriptionPeriod
from erudit.models import Organisation


def get_last_year_of_subscription(organisation):
    if not organisation:
        raise ValueError("Organisation is required")
    period = (
        JournalAccessSubscriptionPeriod.objects.filter(subscription__organisation=organisation)
        .order_by("-end")
        .first()
    )

    if not period:
        return None

    return int(period.end.strftime("%Y"))


def get_last_valid_subscription(organisation):
    """ :returns: the last valid subscription of the organisation """
    subscription = (
        JournalAccessSubscription.valid_objects.institutional()
        .filter(
            organisation=organisation,
        )
        .order_by("-journalaccesssubscriptionperiod__end")
        .first()
    )

    if subscription:
        return subscription

    subscription = (
        JournalAccessSubscription.objects.filter(
            organisation=organisation,
        )
        .order_by("-journalaccesssubscriptionperiod__end")
        .first()
    )

    return subscription


def get_managed_organisations(user):
    """ Returns all the organisation that can be managed by a given user. """
    # Anonymous users cannot be part of an organisation!
    if user.is_anonymous:
        return

    # Superusers or staff members should've access to all organisations while other users'
    # organisations should be determined using Organisation's membership relations.
    if user.is_superuser or user.is_staff:
        return Organisation.objects.all()
    else:
        return user.organisations.all()
