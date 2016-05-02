# -*- coding: utf-8 -*-

from django.db import models


class JournalUpcomingManager(models.Manager):
    def get_queryset(self):
        """ Returns all the upcoming Journal instances. """
        return super(JournalUpcomingManager, self).get_queryset().filter(upcoming=True)
