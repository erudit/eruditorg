# -*- coding: utf-8 -*-

from erudit.models import Journal
from erudit.models import Organisation
from .settings import MANAGED_COLLECTIONS


def get_editable_journals(user):
    """ Given a specific user, returns all the Journal instances he can edit. """
    if user.is_superuser or user.is_staff:
        return Journal.objects.filter(collection__code__in=MANAGED_COLLECTIONS)
    # TODO: add proper permissions checks
    return Journal.objects.filter(members=user)


def get_editable_organisations(user):
    """ Given a specific user, returns all the Organisation instances he can edit. """
    if user.is_superuser or user.is_staff:
        return Organisation.objects.all()
    # TODO: add proper permissions checks
    return user.organisations.all()
