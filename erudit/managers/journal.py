# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q


class LegacyJournalManager(models.Manager):
    """ Provides utility methods to work with journals in the legacy
    databases """

    def get_by_id(self, code):
        """ Return the journal by id

        The legacy system use a different id for scientific and cultural journals
        For scientific journals, the identifier is the code (shortname)
        For cultural journals, the identifier is the fedora localidentifier
        """
        return self.get(Q(code=code) | Q(localidentifier=code))


class JournalUpcomingManager(models.Manager):
    def get_queryset(self):
        """ Returns all the upcoming Journal instances. """
        return super(JournalUpcomingManager, self).get_queryset().filter(upcoming=True)
