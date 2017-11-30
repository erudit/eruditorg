# -*- coding: utf-8 -*-


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

    return organisations.exclude(journalaccesssubscription=None)
