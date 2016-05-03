# -*- coding: utf-8 -*-

from erudit.models import Journal


def get_editable_journals(user):
    """
    Given a specific user, returns all the Journal instances he can edit.
    """
    if user.is_superuser or user.is_staff:
        return Journal.objects.all()
    # TODO: add proper permissions checks
    return Journal.objects.filter(members=user)
