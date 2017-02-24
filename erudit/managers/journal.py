# -*- coding: utf-8 -*-

from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from modeltranslation.manager import MultilingualManager
from polymorphic.manager import PolymorphicManager


class InternalJournalManager(MultilingualManager):
    """ Provides methods to work with journals that are not external.

    That is journals without external URLs. We make the assumption that instances without external
    URLs are instances that should be fully displayed.
    """

    def get_queryset(self):
        """ Returns all the internal Journal instances. """
        return super(InternalJournalManager, self).get_queryset().filter(
            redirect_to_external_url=False
        )


class LegacyJournalManager(MultilingualManager):
    """ Provides utility methods to work with journals in the legacy databases. """

    def get_by_id(self, code):
        """ Return the journal by id

        The legacy system use a different id for scientific and cultural journals
        For scientific journals, the identifier is the code (shortname)
        For cultural journals, the identifier is the fedora localidentifier
        """
        return self.get(Q(code=code) | Q(localidentifier=code))

    def get_by_id_or_404(self, code):
        """ Return the journal or 404 by id

        The legacy system use a different id for scientific and cultural journals
        For scientific journals, the identifier is the code (shortname)
        For cultural journals, the identifier is the fedora localidentifier
        """
        return get_object_or_404(self, Q(code=code) | Q(localidentifier=code))


class UpcomingJournalManager(MultilingualManager):
    """ Provides methods to work with upcoming journals. """

    def get_queryset(self):
        """ Returns all the upcoming Journal instances. """
        return super(UpcomingJournalManager, self).get_queryset().filter(upcoming=True)


class InternalIssueManager(models.Manager):
    """ Provides methods to work with issues that are not external.

    That is issues without external URLs. We make the assumption that instances without external
    URLs are instances that should be fully displayed.
    """

    def get_queryset(self):
        """ Returns all the internal Issue instances. """
        return super(InternalIssueManager, self).get_queryset().filter(external_url__isnull=True)


class InternalArticleManager(PolymorphicManager):
    """ Provides methods to work with articles that are not external.

    That is articles without external URLs. We make the assumption that instances without external
    URLs are instances that should be fully displayed.
    """

    def get_queryset(self):
        """ Returns all the internal Article instances. """
        return super(InternalArticleManager, self).get_queryset().filter(external_url__isnull=True)
