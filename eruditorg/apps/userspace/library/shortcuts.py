# -*- coding: utf-8 -*-

import datetime as dt

from core.subscription.models import JournalAccessSubscription
from erudit.models import Organisation


def get_managed_organisations(user):
    """ Returns all the organisation that can be managed by a given user. """
    # Anonymous users cannot be part of an organisation!
    if user.is_anonymous():
        return

    # Superusers or staff members should've access to all organisations while other users'
    # organisations should be determined using Organisation's membership relations.
    if user.is_superuser or user.is_staff:
        return Organisation.objects.all()
    else:
        organisations = user.organisations.all()

    # Keeps only organisation whose subscription is valid for the current date.
    nowd = dt.datetime.now().date()
    valid_subscriptions = JournalAccessSubscription.objects.filter(
        organisation__in=organisations, journalaccesssubscriptionperiod__start__lte=nowd,
        journalaccesssubscriptionperiod__end__gte=nowd)
    subscribed_organisation_ids = valid_subscriptions.values_list('organisation_id', flat=True)

    return organisations.filter(id__in=subscribed_organisation_ids)
