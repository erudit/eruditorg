# -*- coding: utf-8 -*-

from django.db.models import Q
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
