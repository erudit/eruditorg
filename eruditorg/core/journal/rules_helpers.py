# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q

from erudit.models import Journal
from erudit.models import Organisation
from core.editor.shortcuts import is_production_team_member, get_production_team_journals


def get_editable_journals(user):
    """ Given a specific user, returns all the Journal instances he can edit. """

    if user.is_superuser or user.is_staff:
        return Journal.objects.filter(collection__code__in=settings.MANAGED_COLLECTIONS)

    if is_production_team_member(user):
        production_team_journals = get_production_team_journals(user)
        return Journal.objects.filter(
            Q(members=user) | Q(id__in=production_team_journals)
        )

    # TODO: add proper permissions checks
    return Journal.objects.filter(members=user)


def get_editable_organisations(user):
    """ Given a specific user, returns all the Organisation instances he can edit. """
    if user.is_superuser or user.is_staff:
        return Organisation.objects.all()
    # TODO: add proper permissions checks
    return user.organisations.all()
