# -*- coding: utf-8 -*-

from django.db.models import Q
from ipware.ip import get_ip

from erudit.models import Organisation

from .models import JournalAccessSubscription


def get_journal_organisation_subscribers(journal):
    """ Given a journal returns all the organisations that have subscribed to this journal. """
    organisation_ids = JournalAccessSubscription.valid_objects.filter(
        Q(journal_id=journal.id) | Q(journals__id=journal.id) |
        Q(collection_id=journal.collection_id),
        organisation_id__isnull=False
    ).values_list('organisation_id', flat=True)
    return Organisation.objects.filter(id__in=organisation_ids)


def get_valid_subscription_for_journal(request, journal):
    """ Returns a subscription object if the user has access to the journal. """
    base_subscription_qs = JournalAccessSubscription.valid_objects.filter(
        Q(full_access=True) | Q(journal=journal) | Q(journals__id=journal.id))

    # 1- Is the current user allowed to access the article?
    if not request.user.is_anonymous():
        individual_subscription = base_subscription_qs.filter(user=request.user).first()
        if individual_subscription:
            return individual_subscription

    # 2- Is the current IP address allowed to access the article as an institution?
    ip = get_ip(request)
    institutional_subscription = base_subscription_qs.get_for_ip_address(ip).first()

    return institutional_subscription
